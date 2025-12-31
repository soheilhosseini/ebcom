"""
Language detection using langdetect.
"""

from langdetect import detect, LangDetectException

from src.features.research.domain.enums import DEFAULT_LANGUAGE


class LangDetectLanguageDetector:
    """Language detection using the langdetect library."""
    
    def detect(self, text: str) -> str:
        """Detect the language of input text. Returns ISO 639-1 language code."""
        if not text or not text.strip():
            return DEFAULT_LANGUAGE
        
        try:
            return detect(text)
        except LangDetectException:
            return DEFAULT_LANGUAGE
