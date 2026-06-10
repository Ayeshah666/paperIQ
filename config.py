# config.py
"""
Configuration settings for PaperIQ
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Application configuration"""
    
    # Ollama settings
    OLLAMA_MODEL: str = "llama2"  # or "mistral", "phi", "gemma:2b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    USE_OLLAMA: bool = True  # Fallback to rule-based if False or unavailable
    
    # Analysis thresholds
    ABSTRACT_MIN_WORDS: int = 150
    ABSTRACT_MAX_WORDS: int = 300
    METHODS_MIN_WORDS: int = 200
    RESULTS_MIN_WORDS: int = 150
    
    # Scoring weights
    WEIGHTS = {
        'structure': 0.25,
        'clarity': 0.20,
        'technical_depth': 0.25,
        'methodology': 0.15,
        'results_quality': 0.15
    }
    
    # Technical keywords for validation
    METHODOLOGY_KEYWORDS = [
        'participants', 'sample', 'data collection', 'procedure',
        'materials', 'apparatus', 'statistical analysis', 'measurement',
        'experimental design', 'protocol', 'ethics', 'validation'
    ]
    
    RESULTS_KEYWORDS = [
        'significant', 'p-value', 'mean', 'standard deviation',
        'correlation', 'regression', 'effect size', 'confidence interval',
        'figure', 'table', 'statistical', 'finding'
    ]
    
    # File settings
    MAX_FILE_SIZE_MB: int = 50
    TEMP_DIR: str = "temp"
    
    @classmethod
    def get_ollama_available(cls) -> bool:
        """Check if Ollama is available"""
        import subprocess
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

config = Config()