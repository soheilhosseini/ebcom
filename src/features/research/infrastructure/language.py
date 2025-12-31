"""
Language detection using langdetect.
"""

from langdetect import detect, LangDetectException

from src.features.research.domain.enums import SupportedLanguage
from src.features.research.constants import ARABIC_SCRIPT_LANGUAGES


class LangDetectLanguageDetector:
    """Language detection using the langdetect library."""
    
    def detect(self, text: str) -> str:
        """Detect the language of input text."""
        if not text or not text.strip():
            return SupportedLanguage.get_default().value
        
        try:
            detected = detect(text)
            return self._normalize(detected)
        except LangDetectException:
            return SupportedLanguage.get_default().value
    
    def _normalize(self, detected: str) -> str:
        """Normalize detected language to supported language."""
        if detected == SupportedLanguage.ENGLISH.value:
            return SupportedLanguage.ENGLISH.value
        
        if detected == SupportedLanguage.PERSIAN.value:
            return SupportedLanguage.PERSIAN.value
        
        # Treat Arabic-script languages as Persian
        if detected in ARABIC_SCRIPT_LANGUAGES:
            return SupportedLanguage.PERSIAN.value
        
        return SupportedLanguage.get_default().value
