"""
Property-based test for citation format correctness.

**Feature: research-ai-assistant, Property 10: Citation Format Correctness**
**Validates: Requirements 7.5, 7.6**
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.features.research.domain.models import Citation, FinalReport


url_strategy = st.from_regex(r'https?://[a-z][a-z0-9]*\.[a-z]{2,3}(/[a-z0-9]+)*', fullmatch=True)
title_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S')),
    min_size=1, max_size=200
).filter(lambda x: x.strip())


@given(number=st.integers(min_value=1, max_value=100), title=title_strategy, url=url_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_citation_has_sequential_number(number, title, url):
    """Property 10: Citation has positive integer number."""
    citation = Citation(number=number, title=title, url=url)
    assert isinstance(citation.number, int) and citation.number >= 1


@given(title=title_strategy, url=url_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_citation_has_non_empty_title(title, url):
    """Property 10: Citation has non-empty title."""
    citation = Citation(number=1, title=title, url=url)
    assert isinstance(citation.title, str) and len(citation.title.strip()) > 0


@given(number=st.integers(min_value=1, max_value=100), title=title_strategy, url=url_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_citation_has_valid_url(number, title, url):
    """Property 10: Citation has valid URL."""
    citation = Citation(number=number, title=title, url=url)
    assert citation.url.startswith(('http://', 'https://'))


@given(num_citations=st.integers(min_value=1, max_value=10))
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_citations_have_sequential_numbering(num_citations):
    """Property 10: Citations have sequential numbering starting from 1."""
    citations = [
        Citation(number=i+1, title=f"Title {i+1}", url=f"https://example{i+1}.com")
        for i in range(num_citations)
    ]
    
    report = FinalReport(
        summary="Summary", key_points=["Point"], comparison="Comparison",
        citations=citations, language="en"
    )
    
    for i, citation in enumerate(report.citations):
        assert citation.number == i + 1
