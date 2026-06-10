# utils/report_generator.py
"""
Generate professional reports in multiple formats
"""

from datetime import datetime
from typing import Dict
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

class ReportGenerator:
    """Generate downloadable reports"""
    
    @staticmethod
    def generate_html(analysis: dict, metrics: dict, recommendations: dict) -> str:
        """Generate HTML report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>PaperIQ Analysis Report</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 20px;
                    color: #333;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    text-align: center;
                }}
                .score-card {{
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-left: 4px solid #667eea;
                }}
                .score {{
                    font-size: 48px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .grade {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 25px;
                    font-weight: bold;
                }}
                .section {{
                    margin: 30px 0;
                }}
                .section-title {{
                    font-size: 24px;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .metric-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                }}
                .recommendation-critical {{
                    background: #ffebee;
                    border-left: 4px solid #f44336;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                }}
                .recommendation-important {{
                    background: #fff3e0;
                    border-left: 4px solid #ff9800;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                }}
                .recommendation-suggestion {{
                    background: #e8f5e9;
                    border-left: 4px solid #4caf50;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                }}
                footer {{
                    text-align: center;
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 PaperIQ Analysis Report</h1>
                <p>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
                <div class="grade">Overall Grade: {analysis.get('overall_grade', 'N/A')}</div>
            </div>
            
            <div class="score-card">
                <div class="score">{metrics.get('overall_score', 0):.1f}%</div>
                <p>Overall Quality Score</p>
                <div class="metric-grid">
                    <div class="metric-card">
                        <strong>Structure</strong><br>
                        {metrics.get('structure', 0):.0f}%
                    </div>
                    <div class="metric-card">
                        <strong>Methodology</strong><br>
                        {metrics.get('methodology', {}).get('score', 0):.0f}%
                    </div>
                    <div class="metric-card">
                        <strong>Results</strong><br>
                        {metrics.get('results', {}).get('score', 0):.0f}%
                    </div>
                    <div class="metric-card">
                        <strong>Clarity</strong><br>
                        {metrics.get('clarity', {}).get('score', 0):.0f}%
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">📈 Key Findings</h2>
                <ul>
                    <li><strong>Paper Length:</strong> {analysis.get('paper_stats', {}).get('total_words', 0):,} words over {analysis.get('paper_stats', {}).get('total_pages', 0)} pages</li>
                    <li><strong>Reading Level:</strong> Grade {metrics.get('readability', {}).get('flesch_kincaid_grade', 'N/A')}</li>
                    <li><strong>Sections Complete:</strong> {analysis.get('paper_stats', {}).get('sections_found', 0)}/6 major sections</li>
                </ul>
            </div>
            
            <div class="section">
                <h2 class="section-title">💡 Recommendations</h2>
        """
        
        # Add recommendations
        for rec_type, rec_list in recommendations.items():
            if rec_list:
                class_name = f"recommendation-{rec_type}"
                html += f'<div class="{class_name}"><strong>{rec_type.upper()}:</strong><ul>'
                for rec in rec_list[:5]:  # Limit to top 5
                    html += f'<li>{rec}</li>'
                html += '</ul></div>'
        
        html += """
            </div>
            
            <div class="section">
                <h2 class="section-title">📝 Detailed Metrics</h2>
                <table style="width:100%; border-collapse: collapse;">
        """
        
        # Add metrics table
        methodology = metrics.get('methodology', {})
        results = metrics.get('results', {})
        technical = metrics.get('technical_depth', {})
        
        html += f"""
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Methodology Rigor</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{methodology.get('score', 0):.0f}%</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Statistical Depth</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{results.get('statistical_depth', 'N/A')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Technical Level</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{technical.get('level', 'N/A')}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Citations</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{metrics.get('citations', {}).get('total_references', 0)} references</td></tr>
        """
        
        html += """
                </table>
            </div>
            
            <footer>
                Generated by PaperIQ - AI-Powered Research Paper Analyzer<br>
                This report is for informational purposes only.
            </footer>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def generate_markdown(analysis: dict, metrics: dict, recommendations: dict) -> str:
        """Generate markdown report"""
        md = f"""# 📊 PaperIQ Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Overall Grade:** {analysis.get('overall_grade', 'N/A')}
**Confidence:** {analysis.get('confidence_score', 0):.0f}%

---

## 📈 Overall Score: {metrics.get('overall_score', 0):.1f}%

### Score Breakdown

| Metric | Score |
|--------|-------|
| Structure | {metrics.get('structure', 0):.0f}% |
| Methodology | {metrics.get('methodology', {}).get('score', 0):.0f}% |
| Results | {metrics.get('results', {}).get('score', 0):.0f}% |
| Technical Depth | {metrics.get('technical_depth', {}).get('score', 0):.0f}% |
| Clarity | {metrics.get('clarity', {}).get('score', 0):.0f}% |
| Citations | {metrics.get('citations', {}).get('recency_score', 0):.0f}% |

---

## 📊 Paper Statistics

- **Total Pages:** {analysis.get('paper_stats', {}).get('total_pages', 0)}
- **Total Words:** {analysis.get('paper_stats', {}).get('total_words', 0):,}
- **Sections Found:** {analysis.get('paper_stats', {}).get('sections_found', 0)}/6
- **Est. Reading Time:** {analysis.get('paper_stats', {}).get('estimated_read_time_min', 0)} minutes

---

## 💡 Recommendations

### Critical Issues
"""
        
        for rec in recommendations.get('critical', [])[:5]:
            md += f"- ⚠️ {rec}\n"
        
        md += "\n### Important Improvements\n"
        for rec in recommendations.get('important', [])[:5]:
            md += f"- 🔧 {rec}\n"
        
        md += "\n### Suggestions\n"
        for rec in recommendations.get('suggestions', [])[:5]:
            md += f"- 💡 {rec}\n"
        
        md += f"""

---

## 📝 Additional Insights

- **Readability Level:** Grade {metrics.get('readability', {}).get('flesch_kincaid_grade', 'N/A')}
- **Reading Ease:** {metrics.get('readability', {}).get('flesch_reading_ease', 0):.0f}/100
- **Methodology Components Found:** {sum(metrics.get('methodology', {}).get('components', {}).values())}/6
- **Statistical Analysis:** {'Present' if metrics.get('results', {}).get('metrics', {}).get('has_statistics') else 'Missing'}

---

*Report generated by PaperIQ - AI-Powered Research Paper Analyzer*
"""
        
        return md