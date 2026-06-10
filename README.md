# 📊 PaperIQ - AI-Powered Research Paper Quality Analyzer

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Ollama](https://img.shields.io/badge/Ollama-Ready-orange.svg)](https://ollama.ai/)

PaperIQ is a professional, AI-powered web application that automatically analyzes research papers (PDFs) and provides comprehensive quality metrics, actionable feedback, and AI-powered insights. It helps researchers, students, and academics evaluate and improve their paper quality.

## ✨ Features

### 📊 Comprehensive Analysis
- **Multi-dimensional scoring**: Structure, Methodology, Results, Technical Depth, Clarity, and Citations
- **Real-time metrics**: Readability scores, statistical depth, technical sophistication
- **Interactive visualizations**: Radar charts, gauge charts, and detailed breakdowns

### 🤖 AI-Powered Insights (Optional)
- **Local LLM integration** with Ollama (privacy-focused, no API costs)
- **Intelligent paper summarization**
- **Title suggestions** and improvement recommendations
- **Strengths/weaknesses analysis**

### 📑 Smart PDF Processing
- **Automatic section detection** (Abstract, Methods, Results, Discussion, etc.)
- **Robust text extraction** with cleanup
- **Page and word count statistics**
- **Section distribution analysis**

### 💡 Actionable Feedback
- **Priority-based recommendations** (Critical, Important, Suggestions)
- **Methodology gap analysis**
- **Statistical rigor assessment**
- **Writing clarity evaluation**

### 📥 Export Options
- **HTML report** with professional styling
- **Markdown report** for documentation
- **Shareable analysis results**

## 🚀 Quick Start

### Prerequisites

- **Python 3.9 or higher**
- **pip** (Python package manager)
- **(Optional) Ollama** for AI features

### Installation

1. **Clone the repository**
bash
git clone https://github.com/yourusername/paperiq.git
cd paperiq

2. **Create a virtual environment** (recommended)
bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
3. **Install dependencies**
bash
pip install -r requirements.txt
4. **Install Ollama** (optional - for AI features)
bash
# Visit https://ollama.ai to download
# Or use command line (macOS/Linux):
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (choose one based on your system):
ollama pull llama2      # 3.8GB, good all-around performance
ollama pull mistral     # 4.1GB, faster inference, good accuracy
ollama pull phi         # 1.5GB, lightweight, runs on any system
ollama pull gemma:2b    # 1.5GB, Google's efficient model
5. **Run the application**
```bash
streamlit run app.py
