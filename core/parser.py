# core/parser.py
"""
Advanced PDF parsing with section detection and text cleaning
"""

import re
import PyPDF2
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class Section:
    name: str
    content: str
    start_page: int
    word_count: int = 0
    
    def __post_init__(self):
        self.word_count = len(self.content.split())

class PaperParser:
    """Extract and structure research paper content"""
    
    # Section patterns with priority
    SECTION_PATTERNS = {
        'title': [
            r'(?i)^\s*(?:title|manuscript title)[:\s]*\n?(.+?)(?=\n\n|\n[A-Z])',
            r'(?i)^([A-Z][A-Z\s]{5,50}?)(?=\n)'
        ],
        'abstract': [
            r'(?i)abstract\s*\n-*\s*\n?(.*?)(?=\n\n(?:introduction|keywords|1\.|$))',
            r'(?i)abstract[:\.]?\s*(.*?)(?=\n\n|\n(?:introduction|keywords))'
        ],
        'introduction': [
            r'(?i)(?:1\.\s*|introduction)[:\s]*\n?(.*?)(?=\n\n(?:2\.|methods|methodology|related work))'
        ],
        'methods': [
            r'(?i)(?:2\.\s*|methods|methodology|materials and methods)[:\s]*\n?(.*?)(?=\n\n(?:3\.|results|findings))'
        ],
        'results': [
            r'(?i)(?:3\.\s*|results|findings)[:\s]*\n?(.*?)(?=\n\n(?:4\.|discussion))'
        ],
        'discussion': [
            r'(?i)(?:4\.\s*|discussion)[:\s]*\n?(.*?)(?=\n\n(?:5\.|conclusion|references|$))'
        ],
        'conclusion': [
            r'(?i)(?:5\.\s*|conclusion|conclusions?)[:\s]*\n?(.*?)(?=\n\nreferences|$)'
        ],
        'references': [
            r'(?i)references?\s*\n-*\s*\n?(.*?)$'
        ]
    }
    
    def __init__(self, paper_path: str):
        self.paper_path = paper_path
        self.raw_text = ""
        self.pages = []
        self.sections: Dict[str, Section] = {}
        self._extract_text()
        self._detect_sections()
        
    def _extract_text(self) -> None:
        """Extract text from PDF with page numbers"""
        reader = PyPDF2.PdfReader(self.paper_path)
        self.pages = []
        
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text:
                self.pages.append({
                    'num': page_num,
                    'text': text
                })
                self.raw_text += f"\n{text}"
        
        # Clean text
        self.raw_text = self._clean_text(self.raw_text)
        
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # Remove page headers/footers (common patterns)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        # Fix hyphenated line breaks
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        return text.strip()
    
    def _detect_sections(self) -> None:
        """Detect paper sections using multiple strategies"""
        
        for section_name, patterns in self.SECTION_PATTERNS.items():
            content = ""
            start_page = 1
            
            for pattern in patterns:
                match = re.search(pattern, self.raw_text, re.DOTALL | re.IGNORECASE)
                if match:
                    content = match.group(1).strip()
                    # Find approximate page
                    content_pos = match.start()
                    for page in self.pages:
                        if page['text'] in self.raw_text[content_pos:content_pos+100]:
                            start_page = page['num']
                            break
                    break
            
            if content:
                self.sections[section_name] = Section(
                    name=section_name,
                    content=content,
                    start_page=start_page
                )
            else:
                self.sections[section_name] = Section(
                    name=section_name,
                    content="",
                    start_page=1
                )
    
    def get_section_content(self, section_name: str) -> str:
        """Get content of a specific section"""
        return self.sections.get(section_name, Section(section_name, "", 1)).content
    
    def get_all_sections(self) -> Dict[str, str]:
        """Get all sections as dict of name->content"""
        return {name: sec.content for name, sec in self.sections.items()}
    
    def get_summary_stats(self) -> Dict:
        """Get paper statistics"""
        total_words = sum(len(sec.content.split()) for sec in self.sections.values())
        return {
            'total_pages': len(self.pages),
            'total_words': total_words,
            'sections_found': sum(1 for sec in self.sections.values() if sec.content),
            'estimated_read_time_min': round(total_words / 200)  # 200 wpm
        }