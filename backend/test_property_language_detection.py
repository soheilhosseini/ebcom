"""
Property-based test for language detection accuracy.

**Feature: research-ai-assistant, Property 1: Language Detection Accuracy**
**Validates: Requirements 1.2**

Property 1: Language Detection Accuracy
*For any* input text that is clearly English or Persian, the Language_Detector
SHALL correctly identify the language as "en" or "fa" respectively.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from language_detector import LanguageDetector


# Common English words for generating clearly English text
# Using longer, more distinctive English words for reliable detection
ENGLISH_WORDS = [
    "research", "information", "technology", "computer", "science", "development",
    "analysis", "method", "result", "study", "system", "process", "knowledge",
    "understanding", "application", "implementation", "investigation", "discovery",
    "experiment", "hypothesis", "conclusion", "evidence", "observation", "theory"
]

# Common Persian words for generating clearly Persian text
# Using longer, more distinctive Persian words for reliable detection
PERSIAN_WORDS = [
    "تحقیقات", "اطلاعات", "فناوری", "رایانه", "علمی", "توسعه",
    "تحلیل", "روش", "نتیجه", "مطالعه", "سیستم", "فرآیند", "دانش",
    "درک", "کاربرد", "پیاده‌سازی", "بررسی", "کشف", "آزمایش",
    "فرضیه", "نتیجه‌گیری", "شواهد", "مشاهده", "نظریه", "پژوهش"
]


# Strategy to generate clearly English sentences with enough words for reliable detection
english_sentence_strategy = st.lists(
    st.sampled_from(ENGLISH_WORDS),
    min_size=8,
    max_size=15
).map(lambda words: " ".join(words))


# Strategy to generate clearly Persian sentences with enough words for reliable detection
persian_sentence_strategy = st.lists(
    st.sampled_from(PERSIAN_WORDS),
    min_size=8,
    max_size=15
).map(lambda words: " ".join(words))


@given(english_text=english_sentence_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_english_detection(english_text: str):
    """
    **Feature: research-ai-assistant, Property 1: Language Detection Accuracy**
    **Validates: Requirements 1.2**
    
    For any clearly English text, the Language_Detector SHALL correctly
    identify the language as "en".
    """
    detector = LanguageDetector()
    detected_language = detector.detect(english_text)
    
    assert detected_language == "en", (
        f"Expected 'en' for English text, got '{detected_language}'. "
        f"Input: '{english_text}'"
    )


@given(persian_text=persian_sentence_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_persian_detection(persian_text: str):
    """
    **Feature: research-ai-assistant, Property 1: Language Detection Accuracy**
    **Validates: Requirements 1.2**
    
    For any clearly Persian text, the Language_Detector SHALL correctly
    identify the language as "fa".
    """
    detector = LanguageDetector()
    detected_language = detector.detect(persian_text)
    
    assert detected_language == "fa", (
        f"Expected 'fa' for Persian text, got '{detected_language}'. "
        f"Input: '{persian_text}'"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
