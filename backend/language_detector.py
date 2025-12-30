"""
Language detection module for the Research AI Assistant.

This module provides language detection functionality to identify
whether input text is in English or Persian.
"""

from langdetect import detect, LangDetectException


class LanguageDetector:
    """
    Detects the language of input text.
    
    Supports detection of English ("en") and Persian ("fa").
    Defaults to English if detection fails or language is unsupported.
    """
    
    SUPPORTED_LANGUAGES = {"en", "fa"}
    # Arabic is often confused with Persian by langdetect due to similar scripts
    ARABIC_SCRIPT_LANGUAGES = {"ar", "fa", "ur"}
    DEFAULT_LANGUAGE = "en"
    
    def detect(self, text: str) -> str:
        """
        Detect language of input text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code: "en" for English, "fa" for Persian.
            Defaults to "en" if detection fails or language is unsupported.
        """
        if not text or not text.strip():
            return self.DEFAULT_LANGUAGE
        
        try:
            detected = detect(text)
            # Return detected language if supported
            if detected in self.SUPPORTED_LANGUAGES:
                return detected
            # Treat Arabic-script languages (ar, ur) as Persian since they share similar scripts
            # and langdetect often confuses them
            if detected in self.ARABIC_SCRIPT_LANGUAGES:
                return "fa"
            return self.DEFAULT_LANGUAGE
        except LangDetectException:
            return self.DEFAULT_LANGUAGE
