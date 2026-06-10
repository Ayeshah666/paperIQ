# app.py
"""
PaperIQ - Professional Research Paper Quality Analyzer
Main Streamlit Application
"""

import streamlit as st
import time
from pathlib import Path
import pandas as pd

# Import project modules
from core.analyzer import PaperAnalyzer
from core.parser import PaperParser
from utils.visualizations import Visualizer
from utils.report_generator import ReportGenerator
from config import config

# Page configuration
st.set_page_config(
    page_title="PaperIQ | Research Paper Quality Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .header-title {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        text-align: center;
        margin-top: 0.5rem;
        font-size: 1.1rem;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        transition: transform 0.2s;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-left: 1rem;
        border-left: 4px solid #667eea;
    }
    
    /* Recommendation cards */
    .rec-critical {
        background: linear-gradient(135deg, #ff6b6b10, #ee5a2410);
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .rec-important {
        background: linear-gradient(135deg, #ffa72610, #fb8c0010);
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .rec-suggestion {
        background: linear-gradient(135deg, #66bb6a10, #43a04710);
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Upload area */
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        background: rgba(102, 126, 234, 0.05);
        transition: all 0.3s;
    }
    
    .upload-area:hover {
        background: rgba(102, 126, 234, 0.1);
        border-color: #764ba2;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        color: #666;
        font-size: 0.9rem;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Progress bar customization */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">📊 PaperIQ</h1>
    <p class="header-subtitle">AI-Powered Research Paper Quality Analyzer</p>
    <p class="header-subtitle" style="font-size: 0.9rem; opacity: 0.8;">
        📄 Upload your research paper • 🔍 Get instant quality analysis • 💡 Receive actionable feedback
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    use_llm = st.checkbox(
        "🤖 Enable AI Analysis",
        value=config.USE_OLLAMA,
        help="Use local Ollama for enhanced analysis (requires Ollama installed)"
    )
    
    if use_llm and not config.get_ollama_available():
        st.warning("⚠️ Ollama not detected. Install from https://ollama.ai")
        use_llm = False
    
    st.markdown("---")
    st.markdown("### 📊 About")
    st.info(
        "PaperIQ analyzes your research paper across multiple dimensions:\n\n"
        "• **Structure** - Section completeness\n"
        "• **Methodology** - Research rigor\n"
        "• **Results** - Statistical quality\n"
        "• **Technical Depth** - Sophistication level\n"
        "• **Clarity** - Writing quality\n"
        "• **Citations** - Reference quality\n\n"
        "Supports PDF format only."
    )
    
    st.markdown("---")
    st.markdown("### 🚀 Tips")
    st.success(
        "• Upload papers with clear section headings\n"
        "• Papers should include Abstract, Methods, Results\n"
        "• Longer sections yield more accurate analysis\n"
        "• Install Ollama for AI-powered insights"
    )

# Main content
if not st.session_state.analysis_complete:
    # File upload
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "📄 Drag and drop your research paper PDF here",
            type="pdf",
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        if uploaded_file:
            st.markdown("---")
            st.markdown("### 📋 Paper Details")
            
            # Show file info
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.write(f"**Filename:** {uploaded_file.name}")
            st.write(f"**Size:** {file_size_mb:.2f} MB")
            
            if file_size_mb > config.MAX_FILE_SIZE_MB:
                st.error(f"File too large! Maximum {config.MAX_FILE_SIZE_MB}MB")
                st.stop()
            
            # Analyze button
            if st.button("🔍 Analyze Paper", use_container_width=True):
                # Save temp file
                temp_path = Path("temp") / uploaded_file.name
                temp_path.parent.mkdir(exist_ok=True)
                temp_path.write_bytes(uploaded_file.getbuffer())
                
                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Step 1: Parse PDF
                    status_text.text("📄 Parsing PDF structure...")
                    progress_bar.progress(20)
                    time.sleep(0.5)
                    
                    parser = PaperParser(str(temp_path))
                    
                    # Step 2: Analyze metrics
                    status_text.text("📊 Analyzing metrics...")
                    progress_bar.progress(40)
                    time.sleep(0.3)
                    
                    analyzer = PaperAnalyzer(str(temp_path), use_llm=use_llm)
                    result = analyzer.analyze()
                    
                    # Step 3: Generate insights
                    if use_llm and result.llm_insights:
                        status_text.text("🤖 Generating AI insights...")
                        progress_bar.progress(70)
                        time.sleep(0.5)
                    
                    # Step 4: Prepare results
                    status_text.text("✨ Finalizing analysis...")
                    progress_bar.progress(90)
                    time.sleep(0.3)
                    
                    # Store in session state
                    st.session_state.analysis_result = result
                    st.session_state.analysis_complete = True
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    time.sleep(0.5)
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    st.info("Please ensure your PDF is properly formatted with clear section headings.")
                    
                finally:
                    # Cleanup
                    if temp_path.exists():
                        temp_path.unlink()

else:
    # Display results
    result = st.session_state.analysis_result
    
    # Quick stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666;">Overall Score</div>
            <div class="metric-value">{:.1f}%</div>
            <div style="font-size: 0.9rem; color: {};">Grade: {}</div>
        </div>
        """.format(
            result.metrics['overall_score'],
            '#4caf50' if result.metrics['overall_score'] >= 70 else '#ff9800' if result.metrics['overall_score'] >= 50 else '#f44336',
            result.overall_grade
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666;">Pages</div>
            <div class="metric-value">{}</div>
            <div style="font-size: 0.9rem;">📄 Total pages</div>
        </div>
        """.format(result.paper_stats['total_pages']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666;">Words</div>
            <div class="metric-value">{:,}</div>
            <div style="font-size: 0.9rem;">✍️ Total words</div>
        </div>
        """.format(result.paper_stats['total_words']), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666;">Read Time</div>
            <div class="metric-value">{} min</div>
            <div style="font-size: 0.9rem;">⏱️ Estimated</div>
        </div>
        """.format(result.paper_stats['estimated_read_time_min']), unsafe_allow_html=True)
    
    # Main visualizations
    st.markdown('<div class="section-header">📈 Quality Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        radar_chart = Visualizer.create_radar_chart(result.metrics)
        st.plotly_chart(radar_chart, use_container_width=True)
    
    with col2:
        comparison_chart = Visualizer.create_metrics_comparison(result.metrics)
        st.plotly_chart(comparison_chart, use_container_width=True)
    
    # Section breakdown
    st.markdown('<div class="section-header">📑 Section Analysis</div>', unsafe_allow_html=True)
    
    # Create section metrics
    sections_data = []
    for name, section in result.analysis.parser.sections.items():
        if section.content:
            word_count = len(section.content.split())
            sections_data.append({
                'Section': name.title(),
                'Word Count': word_count,
                'Pages': f"~{word_count // 300 + 1}",
                'Quality': '✅ Complete' if word_count > 100 else '⚠️ Brief' if word_count > 20 else '❌ Insufficient'
            })
    
    if sections_data:
        st.dataframe(
            pd.DataFrame(sections_data),
            use_container_width=True,
            hide_index=True
        )
    
    # Recommendations
    st.markdown('<div class="section-header">💡 Recommendations</div>', unsafe_allow_html=True)
    
    if result.recommendations.get('critical'):
        st.markdown("#### ⚠️ Critical Issues")
        for rec in result.recommendations['critical']:
            st.markdown(f'<div class="rec-critical">• {rec}</div>', unsafe_allow_html=True)
    
    if result.recommendations.get('important'):
        st.markdown("#### 🔧 Important Improvements")
        for rec in result.recommendations['important']:
            st.markdown(f'<div class="rec-important">• {rec}</div>', unsafe_allow_html=True)
    
    if result.recommendations.get('suggestions'):
        st.markdown("#### 💡 Suggestions")
        for rec in result.recommendations['suggestions']:
            st.markdown(f'<div class="rec-suggestion">• {rec}</div>', unsafe_allow_html=True)
    
    # AI Insights (if available)
    if result.llm_insights:
        st.markdown('<div class="section-header">🤖 AI-Powered Insights</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Strengths")
            for strength in result.llm_insights.get('strengths', [])[:5]:
                st.success(f"✅ {strength}")
        
        with col2:
            st.markdown("#### Areas for Improvement")
            for improvement in result.llm_insights.get('improvements', [])[:5]:
                st.warning(f"🎯 {improvement}")
        
        if result.llm_insights.get('suggested_title'):
            st.info(f"**Suggested Title:** {result.llm_insights['suggested_title']}")
    
    # Download options
    st.markdown('<div class="section-header">📥 Export Report</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # HTML Report
        html_report = ReportGenerator.generate_html(
            {
                'overall_grade': result.overall_grade,
                'paper_stats': result.paper_stats,
                'confidence_score': result.confidence_score
            },
            result.metrics,
            result.recommendations
        )
        st.download_button(
            label="📄 Download HTML Report",
            data=html_report,
            file_name=f"paperiq_report_{int(time.time())}.html",
            mime="text/html",
            use_container_width=True
        )
    
    with col2:
        # Markdown Report
        md_report = ReportGenerator.generate_markdown(
            {
                'overall_grade': result.overall_grade,
                'paper_stats': result.paper_stats,
                'confidence_score': result.confidence_score
            },
            result.metrics,
            result.recommendations
        )
        st.download_button(
            label="📝 Download Markdown Report",
            data=md_report,
            file_name=f"paperiq_report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Analyze Another Paper", use_container_width=True):
        st.session_state.analysis_complete = False
        st.session_state.analysis_result = None
        st.rerun()

# Footer
st.markdown("""
<div class="footer">
    <p>PaperIQ v2.0 | AI-Powered Research Paper Quality Analyzer</p>
    <p style="font-size: 0.8rem;">⚡ Powered by Streamlit | 📊 Advanced Analytics | 🤖 Optional LLM Integration</p>
</div>
""", unsafe_allow_html=True)