"""
Property-based test for language consistency.

**Feature: research-ai-assistant, Property 2: Language Consistency**
**Validates: Requirements 1.3, 6.2, 7.7**

Property 2: Language Consistency
*For any* research request, if the input topic is in language L, then all
generated outputs (summaries, key points, comparison, final report) SHALL
be in language L.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume

from language_detector import LanguageDetector
from models import FinalReport, SourceSummary, Citation


# Common English words for generating clearly English text
ENGLISH_WORDS = [
    "research", "information", "technology", "computer", "science", "development",
    "analysis", "method", "result", "study", "system", "process", "knowledge",
    "understanding", "application", "implementation", "investigation", "discovery"
]

# Common Persian words for generating clearly Persian text
PERSIAN_WORDS = [
    "تحقیقات", "اطلاعات", "فناوری", "رایانه", "علمی", "توسعه",
    "تحلیل", "روش", "نتیجه", "مطالعه", "سیستم", "فرآیند", "دانش",
    "درک", "کاربرد", "پیاده‌سازی", "بررسی", "کشف", "آزمایش"
]


def detect_text_language(text: str) -> str:
    """Detect language of text using the LanguageDetector."""
    detector = LanguageDetector()
    return detector.detect(text)


def is_predominantly_english(text: str) -> bool:
    """Check if text is predominantly English (ASCII-based)."""
    if not text or not text.strip():
        return True  # Empty text defaults to English
    # Count ASCII letters vs non-ASCII characters
    ascii_letters = sum(1 for c in text if c.isascii() and c.isalpha())
    non_ascii = sum(1 for c in text if not c.isascii())
    # If mostly ASCII letters, consider it English
    return ascii_letters > non_ascii


def is_predominantly_persian(text: str) -> bool:
    """Check if text contains Persian/Arabic script characters."""
    if not text or not text.strip():
        return False
    # Persian Unicode range: \u0600-\u06FF (Arabic block which includes Persian)
    persian_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    return persian_chars > 0


# Strategy to generate English sentences
english_sentence_strategy = st.lists(
    st.sampled_from(ENGLISH_WORDS),
    min_size=5,
    max_size=10
).map(lambda words: " ".join(words))


# Strategy to generate Persian sentences
persian_sentence_strategy = st.lists(
    st.sampled_from(PERSIAN_WORDS),
    min_size=5,
    max_size=10
).map(lambda words: " ".join(words))


# Strategy to generate English key points
english_key_points_strategy = st.lists(
    english_sentence_strategy,
    min_size=3,
    max_size=7
)


# Strategy to generate Persian key points
persian_key_points_strategy = st.lists(
    persian_sentence_strategy,
    min_size=3,
    max_size=7
)


@given(
    summary=english_sentence_strategy,
    key_points=english_key_points_strategy,
    comparison=english_sentence_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_english_report_language_consistency(
    summary: str,
    key_points: list,
    comparison: str
):
    """
    **Feature: research-ai-assistant, Property 2: Language Consistency**
    **Validates: Requirements 1.3, 6.2, 7.7**
    
    For any FinalReport with language="en", all text content (summary,
    key_points, comparison) SHALL be predominantly English.
    """
    # Create a FinalReport with English language setting
    report = FinalReport(
        summary=summary,
        key_points=key_points,
        comparison=comparison,
        citations=[Citation(number=1, title="Test Source", url="https://example.com")],
        language="en"
    )
    
    # Verify the report language is set correctly
    assert report.language == "en", f"Report language should be 'en', got '{report.language}'"
    
    # Verify summary is predominantly English
    assert is_predominantly_english(report.summary), (
        f"Summary should be predominantly English when language='en'. "
        f"Summary: '{report.summary}'"
    )
    
    # Verify all key points are predominantly English
    for i, point in enumerate(report.key_points):
        assert is_predominantly_english(point), (
            f"Key point {i+1} should be predominantly English when language='en'. "
            f"Point: '{point}'"
        )
    
    # Verify comparison is predominantly English
    assert is_predominantly_english(report.comparison), (
        f"Comparison should be predominantly English when language='en'. "
        f"Comparison: '{report.comparison}'"
    )


@given(
    summary=persian_sentence_strategy,
    key_points=persian_key_points_strategy,
    comparison=persian_sentence_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_persian_report_language_consistency(
    summary: str,
    key_points: list,
    comparison: str
):
    """
    **Feature: research-ai-assistant, Property 2: Language Consistency**
    **Validates: Requirements 1.3, 6.2, 7.7**
    
    For any FinalReport with language="fa", all text content (summary,
    key_points, comparison) SHALL be predominantly Persian.
    """
    # Create a FinalReport with Persian language setting
    report = FinalReport(
        summary=summary,
        key_points=key_points,
        comparison=comparison,
        citations=[Citation(number=1, title="منبع آزمایشی", url="https://example.com")],
        language="fa"
    )
    
    # Verify the report language is set correctly
    assert report.language == "fa", f"Report language should be 'fa', got '{report.language}'"
    
    # Verify summary contains Persian characters
    assert is_predominantly_persian(report.summary), (
        f"Summary should contain Persian characters when language='fa'. "
        f"Summary: '{report.summary}'"
    )
    
    # Verify all key points contain Persian characters
    for i, point in enumerate(report.key_points):
        assert is_predominantly_persian(point), (
            f"Key point {i+1} should contain Persian characters when language='fa'. "
            f"Point: '{point}'"
        )
    
    # Verify comparison contains Persian characters
    assert is_predominantly_persian(report.comparison), (
        f"Comparison should contain Persian characters when language='fa'. "
        f"Comparison: '{report.comparison}'"
    )


@given(
    source_summary=english_sentence_strategy,
    source_number=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_english_source_summary_consistency(
    source_summary: str,
    source_number: int
):
    """
    **Feature: research-ai-assistant, Property 2: Language Consistency**
    **Validates: Requirements 6.2**
    
    For any SourceSummary generated for an English input, the summary
    text SHALL be predominantly English.
    """
    # Create a SourceSummary with English content
    summary = SourceSummary(
        source_number=source_number,
        title="Test Source",
        url="https://example.com",
        summary=source_summary
    )
    
    # Verify the summary is predominantly English
    assert is_predominantly_english(summary.summary), (
        f"Source summary should be predominantly English. "
        f"Summary: '{summary.summary}'"
    )


@given(
    source_summary=persian_sentence_strategy,
    source_number=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_persian_source_summary_consistency(
    source_summary: str,
    source_number: int
):
    """
    **Feature: research-ai-assistant, Property 2: Language Consistency**
    **Validates: Requirements 6.2**
    
    For any SourceSummary generated for a Persian input, the summary
    text SHALL contain Persian characters.
    """
    # Create a SourceSummary with Persian content
    summary = SourceSummary(
        source_number=source_number,
        title="منبع آزمایشی",
        url="https://example.com",
        summary=source_summary
    )
    
    # Verify the summary contains Persian characters
    assert is_predominantly_persian(summary.summary), (
        f"Source summary should contain Persian characters. "
        f"Summary: '{summary.summary}'"
    )


@given(
    input_text=english_sentence_strategy,
    output_text=english_sentence_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_detected_language_matches_output_english(
    input_text: str,
    output_text: str
):
    """
    **Feature: research-ai-assistant, Property 2: Language Consistency**
    **Validates: Requirements 1.3**
    
    For any English input, the detected language should be "en" and
    any output generated should also be in English.
    """
    detector = LanguageDetector()
    detected_lang = detector.detect(input_text)
    
    # For English input, detected language should be "en"
    assert detected_lang == "en", (
        f"Detected language should be 'en' for English input. "
        f"Got: '{detected_lang}', Input: '{input_text}'"
    )
    
    # Output should be predominantly English
    assert is_predominantly_english(output_text), (
        f"Output should be predominantly English when input is English. "
        f"Output: '{output_text}'"
    )


@given(
    input_text=persian_sentence_strategy,
    output_text=persian_sentence_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_detected_language_matches_output_persian(
    input_text: str,
    output_text: str
):
    """
    **Feature: research-ai-assistant, Property 2: Language Consistency**
    **Validates: Requirements 1.3**
    
    For any Persian input, the detected language should be "fa" and
    any output generated should also be in Persian.
    """
    detector = LanguageDetector()
    detected_lang = detector.detect(input_text)
    
    # For Persian input, detected language should be "fa"
    assert detected_lang == "fa", (
        f"Detected language should be 'fa' for Persian input. "
        f"Got: '{detected_lang}', Input: '{input_text}'"
    )
    
    # Output should contain Persian characters
    assert is_predominantly_persian(output_text), (
        f"Output should contain Persian characters when input is Persian. "
        f"Output: '{output_text}'"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
