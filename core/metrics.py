# core/metrics.py
"""
Advanced metrics calculation for research paper quality
"""

import re
import textstat
from typing import Dict, List, Set
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

class MetricsCalculator:
    """Calculate various quality metrics for research papers"""
    
    def __init__(self, sections: Dict[str, str]):
        self.sections = sections
        self.text = " ".join(sections.values())
        
    def calculate_readability(self, text: str) -> Dict:
        """Calculate readability scores"""
        return {
            'flesch_reading_ease': textstat.flesch_reading_ease(text),
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
            'coleman_liau_index': textstat.coleman_liau_index(text),
            'automated_readability_index': textstat.automated_readability_index(text),
            'dale_chall_readability_score': textstat.dale_chall_readability_score(text),
            'difficult_words': textstat.difficult_words(text),
            'sentence_count': textstat.sentence_count(text),
            'avg_sentence_length': textstat.avg_sentence_length(text),
            'avg_syllables_per_word': textstat.avg_syllables_per_word(text)
        }
    
    def calculate_structure_score(self) -> float:
        """Evaluate paper structure completeness"""
        expected_sections = {'abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion'}
        found_sections = set(self.sections.keys())
        
        # Score based on presence and content length
        section_scores = []
        for section in expected_sections:
            if section in self.sections:
                content = self.sections[section]
                words = len(content.split())
                if words > 50:  # Substantial content
                    section_scores.append(1.0)
                elif words > 10:
                    section_scores.append(0.5)
                else:
                    section_scores.append(0.2)
            else:
                section_scores.append(0.0)
        
        return sum(section_scores) / len(expected_sections) * 100
    
    def calculate_methodology_rigor(self) -> Dict:
        """Evaluate methodology section quality"""
        methods = self.sections.get('methods', '')
        methods_lower = methods.lower()
        
        # Check for key methodological components
        components = {
            'participants/sample': any(word in methods_lower for word in ['participant', 'sample', 'subject', 'patient']),
            'data collection': any(word in methods_lower for word in ['data collection', 'collect', 'measure']),
            'procedure': any(word in methods_lower for word in ['procedure', 'protocol', 'step', 'process']),
            'materials': any(word in methods_lower for word in ['material', 'apparatus', 'equipment', 'tool']),
            'statistical analysis': any(word in methods_lower for word in ['statistical', 'analysis', 'test', 'p-value']),
            'ethics approval': any(word in methods_lower for word in ['ethics', 'approval', 'consent', 'institutional review'])
        }
        
        score = sum(components.values()) / len(components) * 100
        
        return {
            'score': score,
            'components': components,
            'word_count': len(methods.split()),
            'recommendations': self._get_methodology_recommendations(components)
        }
    
    def _get_methodology_recommendations(self, components: Dict) -> List[str]:
        """Generate recommendations based on missing components"""
        recommendations = []
        if not components['participants/sample']:
            recommendations.append("Describe your participant/sample characteristics")
        if not components['data collection']:
            recommendations.append("Detail your data collection procedures")
        if not components['procedure']:
            recommendations.append("Provide step-by-step experimental procedures")
        if not components['materials']:
            recommendations.append("List all materials and equipment used")
        if not components['statistical analysis']:
            recommendations.append("Include statistical analysis methods")
        if not components['ethics approval']:
            recommendations.append("Mention ethics approval and consent procedures")
        return recommendations
    
    def calculate_results_quality(self) -> Dict:
        """Evaluate results section quality"""
        results = self.sections.get('results', '')
        results_lower = results.lower()
        
        # Check for statistical and data presentation
        metrics = {
            'has_statistics': bool(re.search(r'p\s*[<=>]|p-value|significant|mean|sd|±', results_lower)),
            'has_numbers': bool(re.search(r'\d+(?:\.\d+)?', results)),
            'has_tables_figures': bool(re.search(r'(table|figure|fig\.)\s*\d+', results_lower)),
            'has_comparisons': bool(re.search(r'(higher|lower|greater|less|increase|decrease|compared)', results_lower)),
            'has_confidence_intervals': bool(re.search(r'ci|confidence interval', results_lower)),
            'has_effect_sizes': bool(re.search(r'effect size|cohen|d\s*=', results_lower))
        }
        
        score = sum(metrics.values()) / len(metrics) * 100
        
        return {
            'score': score,
            'metrics': metrics,
            'statistical_depth': 'high' if metrics['has_statistics'] and metrics['has_effect_sizes'] else 'medium' if metrics['has_statistics'] else 'low',
            'visual_richness': 'high' if metrics['has_tables_figures'] else 'low',
            'word_count': len(results.split())
        }
    
    def calculate_citation_quality(self) -> Dict:
        """Analyze citation patterns"""
        references = self.sections.get('references', '')
        
        # Count references
        ref_count = references.count('\n[') + references.count('\n1.') + 1 if references else 0
        
        # Check for recent references
        recent_refs = len(re.findall(r'(202[0-9]|202[0-9]|2019)', references))
        
        return {
            'total_references': ref_count,
            'recent_references': recent_refs,
            'has_references': ref_count > 0,
            'recency_score': min(100, (recent_refs / max(1, ref_count)) * 100) if ref_count > 0 else 0
        }
    
    def calculate_technical_depth(self) -> Dict:
        """Measure technical sophistication"""
        text = self.text
        
        # Technical vocabulary indicators
        indicators = {
            'jargon_density': self._calculate_jargon_density(text),
            'equation_presence': bool(re.search(r'\$.*\$|\\[a-z]+|equation|formula', text, re.IGNORECASE)),
            'code_or_algorithms': bool(re.search(r'algorithm|pseudocode|def\s+\w+|function', text, re.IGNORECASE)),
            'mathematical_expressions': bool(re.search(r'[=<>~]\s*[0-9\.]+\s*[+\-*/]', text)),
            'field_specific_terms': self._count_field_terms(text)
        }
        
        score = (indicators['jargon_density'] * 0.4 + 
                indicators['equation_presence'] * 0.2 +
                indicators['code_or_algorithms'] * 0.2 +
                indicators['mathematical_expressions'] * 0.2) * 100
        
        return {
            'score': min(100, score),
            'indicators': indicators,
            'level': 'advanced' if score > 70 else 'intermediate' if score > 40 else 'basic'
        }
    
    def _calculate_jargon_density(self, text: str) -> float:
        """Calculate technical jargon density"""
        # Common technical terms in research
        jargon_terms = {
            'analysis', 'methodology', 'correlation', 'regression', 'significant',
            'variable', 'hypothesis', 'empirical', 'theoretical', 'framework',
            'algorithm', 'optimization', 'parameter', 'validation', 'robustness',
            'significance', 'statistical', 'quantitative', 'qualitative', 'synthesis'
        }
        
        words = set(text.lower().split())
        jargon_count = len(words.intersection(jargon_terms))
        return min(1.0, jargon_count / 20)  # Normalize
    
    def _count_field_terms(self, text: str) -> int:
        """Count field-specific terminology"""
        # This can be extended based on research field
        terms = re.findall(r'\b(?:analysis|system|model|method|approach|technique|algorithm|framework)\b', text.lower())
        return len(terms)
    
    def calculate_clarity_score(self) -> Dict:
        """Evaluate writing clarity"""
        readability = self.calculate_readability(self.text)
        
        # Ideal readability for academic papers: grade 10-14
        grade = readability['flesch_kincaid_grade']
        grade_score = 100 - min(100, abs(grade - 12) * 10)
        
        # Sentence length penalty
        sentences = readability['sentence_count']
        long_sentences = len([s for s in self.text.split('.') if len(s.split()) > 30])
        sentence_score = max(0, 100 - (long_sentences / max(1, sentences)) * 50)
        
        clarity_score = (grade_score * 0.4 + sentence_score * 0.4 + 
                        (100 - readability['difficult_words'] / 20) * 0.2)
        
        return {
            'score': clarity_score,
            'readability_grade': grade,
            'reading_ease': readability['flesch_reading_ease'],
            'sentence_variety': 'good' if long_sentences / max(1, sentences) < 0.3 else 'needs improvement',
            'recommendations': self._get_clarity_recommendations(readability)
        }
    
    def _get_clarity_recommendations(self, readability: Dict) -> List[str]:
        """Generate writing clarity recommendations"""
        recommendations = []
        if readability['flesch_reading_ease'] < 30:
            recommendations.append("Consider simplifying complex sentences")
        if readability['avg_sentence_length'] > 25:
            recommendations.append("Break down long sentences for better readability")
        if readability['difficult_words'] > 50:
            recommendations.append("Define technical terms when first introduced")
        if readability['flesch_kincaid_grade'] > 14:
            recommendations.append("Aim for more accessible academic writing")
        return recommendations
    
    def generate_comprehensive_metrics(self) -> Dict:
        """Generate all metrics"""
        structure_score = self.calculate_structure_score()
        methodology = self.calculate_methodology_rigor()
        results = self.calculate_results_quality()
        citations = self.calculate_citation_quality()
        technical = self.calculate_technical_depth()
        clarity = self.calculate_clarity_score()
        
        # Overall score (weighted average)
        overall = (
            structure_score * 0.15 +
            methodology['score'] * 0.20 +
            results['score'] * 0.20 +
            citations['recency_score'] * 0.10 +
            technical['score'] * 0.20 +
            clarity['score'] * 0.15
        )
        
        return {
            'overall_score': round(overall, 1),
            'structure': round(structure_score, 1),
            'methodology': methodology,
            'results': results,
            'citations': citations,
            'technical_depth': technical,
            'clarity': clarity,
            'readability': self.calculate_readability(self.text)
        }