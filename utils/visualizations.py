# utils/visualizations.py
"""
Professional visualizations for paper analysis
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class Visualizer:
    """Create professional visualizations for the analysis"""
    
    @staticmethod
    def create_radar_chart(metrics: dict) -> go.Figure:
        """Create a radar chart for multi-dimensional metrics"""
        categories = ['Structure', 'Methodology', 'Results', 'Technical\nDepth', 'Clarity', 'Citations']
        
        values = [
            metrics.get('structure', 0),
            metrics.get('methodology', {}).get('score', 0),
            metrics.get('results', {}).get('score', 0),
            metrics.get('technical_depth', {}).get('score', 0),
            metrics.get('clarity', {}).get('score', 0),
            metrics.get('citations', {}).get('recency_score', 0)
        ]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]],  # Close the loop
            theta=categories + [categories[0]],
            fill='toself',
            marker=dict(color='rgba(106, 120, 209, 0.8)'),
            line=dict(color='#6a78d1', width=2),
            name='Paper Score'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
            visible=True,
                    range=[0, 100],
                    tickfont=dict(size=10)
                ),
                angularaxis=dict(
                    tickfont=dict(size=11, weight='bold')
                )
            ),
            showlegend=False,
            height=450,
            margin=dict(l=80, r=80, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    @staticmethod
    def create_gauge_chart(value: float, title: str, max_value: int = 100) -> go.Figure:
        """Create a gauge chart for single metrics"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title, 'font': {'size': 14}},
            gauge={
                'axis': {'range': [0, max_value], 'tickwidth': 1},
                'bar': {'color': "#6a78d1"},
                'steps': [
                    {'range': [0, 33], 'color': "#ffebee"},
                    {'range': [33, 66], 'color': "#fff3e0"},
                    {'range': [66, 100], 'color': "#e8f5e9"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        ))
        
        fig.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    @staticmethod
    def create_metrics_comparison(metrics: dict) -> go.Figure:
        """Create a bar chart comparing different metrics"""
        categories = []
        scores = []
        
        metric_mapping = {
            'Structure': metrics.get('structure', 0),
            'Methodology': metrics.get('methodology', {}).get('score', 0),
            'Results': metrics.get('results', {}).get('score', 0),
            'Technical': metrics.get('technical_depth', {}).get('score', 0),
            'Clarity': metrics.get('clarity', {}).get('score', 0),
        }
        
        for cat, score in metric_mapping.items():
            categories.append(cat)
            scores.append(score)
        
        colors = ['#6a78d1' if s >= 70 else '#ff9800' if s >= 50 else '#f44336' for s in scores]
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=scores,
                marker_color=colors,
                text=[f'{s:.1f}%' for s in scores],
                textposition='outside',
                hovertemplate='%{x}: %{y:.1f}%<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="Metric Performance",
            yaxis_title="Score (%)",
            yaxis_range=[0, 100],
            height=400,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        
        return fig
    
    @staticmethod
    def create_section_word_cloud(sections: dict) -> go.Figure:
        """Create a treemap of section word counts"""
        data = []
        for name, content in sections.items():
            if content:
                word_count = len(content.split())
                data.append({
                    'Section': name.title(),
                    'Word Count': word_count,
                    'Percentage': word_count / max(1, sum(len(c.split()) for c in sections.values())) * 100
                })
        
        if not data:
            return go.Figure()
        
        df = pd.DataFrame(data)
        
        fig = px.treemap(
            df,
            path=['Section'],
            values='Word Count',
            color='Percentage',
            color_continuous_scale='Blues',
            title="Content Distribution by Section"
        )
        
        fig.update_layout(
            height=350,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    @staticmethod
    def create_quality_dashboard(metrics: dict, stats: dict) -> go.Figure:
        """Create a comprehensive quality dashboard"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Overall Score', 'Readability Grade', 'Paper Stats', 'Recommendation Priority'),
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}],
                   [{'type': 'table'}, {'type': 'bar'}]]
        )
        
        # Overall Score
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=metrics.get('overall_score', 0),
                delta={'reference': 70},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#6a78d1"},
                    'steps': [
                        {'range': [0, 50], 'color': "#ffebee"},
                        {'range': [50, 75], 'color': "#fff3e0"},
                        {'range': [75, 100], 'color': "#e8f5e9"}
                    ]
                }
            ),
            row=1, col=1
        )
        
        # Readability Grade
        grade = metrics.get('readability', {}).get('flesch_kincaid_grade', 12)
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=grade,
                title={'text': "Grade Level"},
                number={'suffix': "th grade"}
            ),
            row=1, col=2
        )
        
        # Paper Stats table
        stats_data = [
            ['Total Pages', stats.get('total_pages', 0)],
            ['Total Words', f"{stats.get('total_words', 0):,}"],
            ['Sections Found', stats.get('sections_found', 0)],
            ['Est. Read Time', f"{stats.get('estimated_read_time_min', 0)} min"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value'], align='left'),
                cells=dict(values=list(zip(*stats_data)), align='left')
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=11)
        )
        
        return fig