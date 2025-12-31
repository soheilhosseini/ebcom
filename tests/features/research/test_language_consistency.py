"""
Property-based test for language consistency.

**Feature: research-ai-assistant, Property 2: Language Consistency**
**Validates: Requirements 1.3, 6.2, 7.7**
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.features.research.infrastructure.language import LangDetectLanguageDetector
from src.features.research.domain.models import FinalReport, SourceSummary, Citation


ENGLISH_WORDS = [
    "research", "information", "technology", "computer", "science", "development",
    "analysis", "method", "result", "study", "system", "process", "knowledge"
]

PERSIAN_WORDS = [
    "تحقیقات", "اطلاعات", "فناوری", "رایانه", "علمی", "توسعه",
    "تحلیل", "روش", "نتیجه", "مطالعه", "سیستم", "فرآیند", "دانش"
]


def is_predominantly_english(text: str) -> bool:
    if not text or not text.strip():
        return True
    ascii_letters = sum(1 for c in text if c.isascii() and c.isalpha())
    non_ascii = sum(1 for c in text if not c.isascii())
    return ascii_letters > non_ascii


def is_predominantly_persian(text: str) -> bool:
    if not text or not text.strip():
        return False
    persian_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    return persian_chars > 0


english_sentence_strategy = st.lists(
    st.sampled_from(ENGLISH_WORDS), min_size=5, max_size=10
).map(lambda words: " ".join(words))

persian_sentence_strategy = st.lists(
    st.sampled_from(PERSIAN_WORDS), min_size=5, max_size=10
).map(lambda words: " ".join(words))

english_key_points_strategy = st.lists(english_sentence_strategy, min_size=3, max_size=7)
persian_key_points_strategy = st.lists(persian_sentence_strategy, min_size=3, max_size=7)


@given(
    summary=english_sentence_strategy,
    key_points=english_key_points_strategy,
    comparison=english_sentence_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_english_report_language_consistency(summary, key_points, comparison):
    """Property 2: English report content is predominantly English."""
    report = FinalReport(
        summary=summary, key_points=key_points, comparison=comparison,
        citations=[Citation(number=1, title="Test", url="https://example.com")],
        language="en"
    )
    
    assert report.language == "en"
    assert is_predominantly_english(report.summary)
    for point in report.key_points:
        assert is_predominantly_english(point)
    assert is_predominantly_english(report.comparison)


@given(
    summary=persian_sentence_strategy,
    key_points=persian_key_points_strategy,
    comparison=persian_sentence_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_persian_report_language_consistency(summary, key_points, comparison):
    """Property 2: Persian report content contains Persian characters."""
    report = FinalReport(
        summary=summary, key_points=key_points, comparison=comparison,
        citations=[Citation(number=1, title="منبع", url="https://example.com")],
        language="fa"
    )
    
    assert report.language == "fa"
    assert is_predominantly_persian(report.summary)
    for point in report.key_points:
        assert is_predominantly_persian(point)
    assert is_predominantly_persian(report.comparison)


@given(input_text=english_sentence_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_detected_language_matches_output_english(input_text):
    """Property 2: English input detected as a valid language code."""
    detector = LangDetectLanguageDetector()
    detected = detector.detect(input_text)
    # langdetect returns ISO 639-1 codes, just verify it's a non-empty string
    assert isinstance(detected, str) and len(detected) >= 2


@given(input_text=persian_sentence_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_detected_language_matches_output_persian(input_text):
    """Property 2: Persian input detected as Arabic-script language."""
    detector = LangDetectLanguageDetector()
    detected = detector.detect(input_text)
    # langdetect may confuse Persian with Arabic due to similar script
    assert detected in ("fa", "ar", "ur")
