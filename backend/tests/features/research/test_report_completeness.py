"""
Property-based test for report completeness.

**Feature: research-ai-assistant, Property 9: Report Completeness**
**Validates: Requirements 7.2, 7.3, 7.4**
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.features.research.domain.models import FinalReport, Citation


non_empty_text_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S', 'Z')),
    min_size=10, max_size=500
).filter(lambda x: x.strip())

citation_strategy = st.builds(
    Citation,
    number=st.integers(min_value=1, max_value=100),
    title=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    url=st.from_regex(r'https?://[a-z]+\.[a-z]{2,3}(/[a-z0-9]+)*', fullmatch=True)
)

citations_list_strategy = st.lists(citation_strategy, min_size=1, max_size=10)
key_points_strategy = st.lists(non_empty_text_strategy, min_size=1, max_size=10)
language_strategy = st.sampled_from(["en", "fa"])


@given(
    summary=non_empty_text_strategy,
    key_points=key_points_strategy,
    comparison=non_empty_text_strategy,
    citations=citations_list_strategy,
    language=language_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_report_has_all_required_sections(summary, key_points, comparison, citations, language):
    """Property 9: Report contains all required sections."""
    report = FinalReport(
        summary=summary, key_points=key_points, comparison=comparison,
        citations=citations, language=language
    )
    
    assert hasattr(report, 'summary') and report.summary
    assert hasattr(report, 'key_points') and isinstance(report.key_points, list) and len(report.key_points) > 0
    assert hasattr(report, 'comparison') and report.comparison
    assert hasattr(report, 'citations') and isinstance(report.citations, list) and len(report.citations) > 0


@given(
    num_key_points=st.integers(min_value=1, max_value=15),
    num_citations=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_report_preserves_key_points_count(num_key_points, num_citations):
    """Property 9: Key points and citations counts preserved."""
    key_points = [f"Key point {i+1}" for i in range(num_key_points)]
    citations = [Citation(number=i+1, title=f"Source {i+1}", url=f"https://example{i+1}.com") for i in range(num_citations)]
    
    report = FinalReport(
        summary="Summary", key_points=key_points, comparison="Comparison",
        citations=citations, language="en"
    )
    
    assert len(report.key_points) == num_key_points
    assert len(report.citations) == num_citations


@given(summary_text=non_empty_text_strategy, comparison_text=non_empty_text_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_report_content_integrity(summary_text, comparison_text):
    """Property 9: Summary and comparison content preserved."""
    report = FinalReport(
        summary=summary_text, key_points=["Point"], comparison=comparison_text,
        citations=[Citation(number=1, title="Test", url="https://test.com")],
        language="en"
    )
    
    assert report.summary == summary_text
    assert report.comparison == comparison_text
