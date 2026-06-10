# core/analyzer.py - Complete working version
from .parser import PaperParser
from .metrics import MetricsCalculator
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class AnalysisReport:
    """Complete analysis report data structure"""
    paper_stats: Dict
    metrics: Dict
    llm_insights: Dict
    recommendations: Dict
    overall_grade: str
    confidence_score: float
    analysis: Optional['PaperAnalyzer'] = None

class PaperAnalyzer:
    """Orchestrate comprehensive paper analysis"""
    
    GRADE_THRESHOLDS = {
        'A+': 95, 'A': 90, 'A-': 85,
        'B+': 80, 'B': 75, 'B-': 70,
        'C+': 65, 'C': 60, 'D': 50, 'F': 0
    }
    
    def __init__(self, paper_path: str, use_llm: bool = True):
        self.paper_path = paper_path
        self.parser = PaperParser(paper_path)
        self.metrics = MetricsCalculator(self.parser.get_all_sections())
        self.use_llm = use_llm
        self.llm = None
        
        # Try to import LLM if requested
        if use_llm:
            try:
                from .llm_integration import LLMAnalyzer
                self.llm = LLMAnalyzer()
                print(f"LLM loaded, available: {self.llm.available}")
            except ImportError as e:
                print(f"Could not import LLMAnalyzer: {e}")
            except Exception as e:
                print(f"Error initializing LLM: {e}")
        
        self.analysis = self
        
    def analyze(self) -> AnalysisReport:
        """Run complete analysis"""
        
        # Calculate all metrics
        metrics = self.metrics.generate_comprehensive_metrics()
        
        # Get LLM insights if available
        llm_insights = {}
        if self.llm and self.llm.available:
            try:
                sections = self.parser.get_all_sections()
                llm_insights = self.llm.analyze_strengths_weaknesses(sections)
                
                # Generate summary from abstract or intro
                abstract = self.parser.get_section_content('abstract')
                if abstract:
                    llm_insights['summary'] = self.llm.generate_summary(abstract)
                else:
                    intro = self.parser.get_section_content('introduction')
                    if intro:
                        llm_insights['summary'] = self.llm.generate_summary(intro)
                
                # Suggest title
                if abstract:
                    llm_insights['suggested_title'] = self.llm.suggest_title(abstract)
                    
            except Exception as e:
                print(f"Error getting LLM insights: {e}")
                llm_insights = {}
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, llm_insights)
        
        # Calculate overall grade
        overall_grade = self._calculate_grade(metrics['overall_score'])
        
        # Confidence score based on section completeness
        sections_found = sum(1 for s in self.parser.sections.values() if s and len(s) > 50)
        confidence = min(95, 60 + sections_found * 5)
        
        return AnalysisReport(
            paper_stats=self.parser.get_summary_stats(),
            metrics=metrics,
            llm_insights=llm_insights,
            recommendations=recommendations,
            overall_grade=overall_grade,
            confidence_score=confidence,
            analysis=self
        )
    
    def _generate_recommendations(self, metrics: Dict, llm_insights: Dict) -> Dict:
        """Generate actionable recommendations"""
        recommendations = {
            'critical': [],
            'important': [],
            'suggestions': []
        }
        
        # Structure recommendations
        if metrics['structure'] < 60:
            recommendations['critical'].append(
                "Paper missing essential sections. Ensure all standard sections are present."
            )
        elif metrics['structure'] < 80:
            recommendations['important'].append(
                "Some sections are brief. Expand each section with more detailed content."
            )
        
        # Methodology recommendations
        methodology_score = metrics['methodology']['score']
        if methodology_score < 50:
            recommendations['critical'].extend(metrics['methodology']['recommendations'][:2])
        elif methodology_score < 75:
            recommendations['important'].extend(metrics['methodology']['recommendations'][:2])
        else:
            for rec in metrics['methodology']['recommendations'][:1]:
                recommendations['suggestions'].append(rec)
        
        # Results recommendations
        if not metrics['results']['metrics'].get('has_statistics', False):
            recommendations['important'].append(
                "Include statistical analyses to support your findings"
            )
        if not metrics['results']['metrics'].get('has_tables_figures', False):
            recommendations['suggestions'].append(
                "Consider adding visual elements (tables/figures) to present results"
            )
        
        # Citation recommendations
        if metrics['citations']['total_references'] < 15:
            recommendations['important'].append(
                f"Only {metrics['citations']['total_references']} references found. Aim for 20-40 citations."
            )
        
        # Clarity recommendations
        if metrics['clarity'].get('recommendations', []):
            for rec in metrics['clarity']['recommendations'][:2]:
                recommendations['important'].append(rec)
        
        # Add LLM insights if available
        if llm_insights.get('improvements'):
            for improvement in llm_insights['improvements'][:2]:
                if improvement not in recommendations['important']:
                    recommendations['important'].append(improvement)
        
        return recommendations
    
    def _calculate_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        for grade, threshold in self.GRADE_THRESHOLDS.items():
            if score >= threshold:
                return grade
        return 'F'