# core/llm_integration.py
"""
Local Ollama integration for intelligent paper analysis
"""

import json
import subprocess
from typing import Dict, Optional, List
import requests

class LLMAnalyzer:
    """Integrate with local Ollama for advanced analysis"""
    
    def __init__(self, model_name: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.available = self._check_availability()
        
    def _check_availability(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(m.get('name', '').startswith(self.model_name) for m in models)
            return False
        except:
            return False
    
    def analyze_strengths_weaknesses(self, sections: Dict[str, str]) -> Dict:
        """Use LLM to analyze paper strengths and weaknesses"""
        if not self.available:
            return self._fallback_analysis(sections)
        
        prompt = f"""Analyze this research paper and identify:
        1. Three main strengths
        2. Three areas for improvement
        3. Overall quality assessment
        
        Abstract: {sections.get('abstract', '')[:500]}
        Methods: {sections.get('methods', '')[:500]}
        Results: {sections.get('results', '')[:500]}
        
        Respond in JSON format with keys: strengths, improvements, assessment
        """
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_llm_response(result.get('response', ''))
        except Exception as e:
            print(f"LLM analysis failed: {e}")
        
        return self._fallback_analysis(sections)
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM JSON response"""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(response[json_start:json_end])
        except:
            pass
        
        # Fallback parsing
        return {
            'strengths': ['Well-structured content', 'Clear methodology', 'Comprehensive analysis'],
            'improvements': ['Consider more citations', 'Add statistical validation', 'Expand discussion'],
            'assessment': 'Good quality paper with room for improvement'
        }
    
    def _fallback_analysis(self, sections: Dict[str, str]) -> Dict:
        """Rule-based fallback analysis"""
        strengths = []
        improvements = []
        
        abstract = sections.get('abstract', '')
        methods = sections.get('methods', '')
        results = sections.get('results', '')
        
        if len(abstract.split()) > 100:
            strengths.append("Comprehensive abstract")
        else:
            improvements.append("Expand abstract with key findings")
        
        if len(methods.split()) > 200:
            strengths.append("Detailed methodology section")
        else:
            improvements.append("Add more methodological details")
        
        if len(results.split()) > 150:
            strengths.append("Substantial results presentation")
        else:
            improvements.append("Expand results with more data")
        
        return {
            'strengths': strengths or ["Good overall structure"],
            'improvements': improvements or ["Consider adding more statistical analysis"],
            'assessment': "Paper shows good foundational elements"
        }
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate intelligent summary using LLM"""
        if not self.available:
            return self._simple_summary(text, max_length)
        
        prompt = f"Summarize this research paper in {max_length} words or less:\n\n{text[:2000]}"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": max_length * 2}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                summary = response.json().get('response', '')
                return summary[:max_length] + ("..." if len(summary) > max_length else "")
        except:
            pass
        
        return self._simple_summary(text, max_length)
    
    def _simple_summary(self, text: str, max_length: int) -> str:
        """Simple extractive summary"""
        sentences = text.split('. ')
        # Take first few sentences that contain key terms
        key_sentences = []
        key_terms = ['paper', 'study', 'research', 'method', 'result', 'conclusion']
        
        for sent in sentences:
            if any(term in sent.lower() for term in key_terms):
                key_sentences.append(sent)
                if len(' '.join(key_sentences)) > max_length:
                    break
        
        summary = '. '.join(key_sentences[:3])
        return summary[:max_length] + ("..." if len(summary) > max_length else "")
    
    def suggest_title(self, abstract: str) -> str:
        """Suggest improved title using LLM"""
        if not self.available:
            return "Research Paper Analysis"
        
        prompt = f"Suggest a concise, impactful title for a research paper with this abstract:\n\n{abstract[:500]}"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 50}
                },
                timeout=20
            )
            
            if response.status_code == 200:
                return response.json().get('response', '').strip()[:80]
        except:
            pass
        
        return "Research Paper Quality Analysis"