"""
Property-based test for citation format correctness.

**Feature: research-ai-assistant, Property 10: Citation Format Correctness**
**Validates: Requirements 7.5, 7.6**

Property 10: Citation Format Correctness
*For any* citation in the final report, it SHALL have a sequential number
starting from 1, a non-empty title, and a valid URL.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from models import Citation, FinalReport


# Strategy to generate valid URLs
url_strategy = st.from_regex(
    r'https?://[a-z][a-z0-9]*\.[a-z]{2,3}(/[a-z0-9]+)*',
    fullmatch=True
)

# Strategy to generate non-empty titles
title_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S')),
    min_size=1,
    max_size=200
).filter(lambda x: x.strip())


@given(
    number=st.integers(min_value=1, max_value=100),
    title=title_strategy,
    url=url_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_citation_has_sequential_number(number: int, title: str, url: str):
    """
    **Feature: research-ai-assistant, Property 10: Citation Format Correctness**
    **Validates: Requirements 7.5**
    
    For any citation, it SHALL have a number that is a positive integer.
    """
    citation = Citation(number=number, title=title, url=url)
    
    # Verify number is a positive integer
    assert isinstance(citation.number, int), "Citation number must be an integer"
    assert citation.number >= 1, "Citation number must be at least 1"


@given(
    title=title_strategy,
    url=url_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_citation_has_non_empty_title(title: str, url: str):
    """
    **Feature: research-ai-assistant, Property 10: Citation Format Correctness**
    **Validates: Requirements 7.6**
    
    For any citation, it SHALL have a non-empty title.
    """
    citation = Citation(number=1, title=title, url=url)
    
    # Verify title is non-empty
    assert isinstance(citation.title, str), "Citation title must be a string"
    assert len(citation.title) > 0, "Citation title must not be empty"
    assert len(citation.title.strip()) > 0, "Citation title must not be whitespace only"


@given(
    number=st.integers(min_value=1, max_value=100),
    title=title_strategy,
    url=url_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_citation_has_valid_url(number: int, title: str, url: str):
    """
    **Feature: research-ai-assistant, Property 10: Citation Format Correctness**
    **Validates: Requirements 7.6**
    
    For any citation, it SHALL have a valid URL starting with http:// or https://.
    """
    citation = Citation(number=number, title=title, url=url)
    
    # Verify URL is a string
    assert isinstance(citation.url, str), "Citation URL must be a string"
    
    # Verify URL is non-empty
    assert len(citation.url) > 0, "Citation URL must not be empty"
    
    # Verify URL starts with http:// or https://
    assert citation.url.startswith(('http://', 'https://')), (
        f"Citation URL must start with http:// or https://, got: {citation.url}"
    )


@given(
    num_citations=st.integers(min_value=1, max_value=10)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_citations_have_sequential_numbering(num_citations: int):
    """
    **Feature: research-ai-assistant, Property 10: Citation Format Correctness**
    **Validates: Requirements 7.5**
    
    For any list of citations in a report, the numbers SHALL be sequential
    starting from 1.
    """
    # Create citations with sequential numbering
    citations = [
        Citation(
            number=i + 1,
            title=f"Source Title {i + 1}",
            url=f"https://example{i + 1}.com/article"
        )
        for i in range(num_citations)
    ]
    
    # Create a report with these citations
    report = FinalReport(
        summary="Test summary for the research topic.",
        key_points=["Key point 1", "Key point 2"],
        comparison="Comparison of sources.",
        citations=citations,
        language="en"
    )
    
    # Verify sequential numbering starting from 1
    for i, citation in enumerate(report.citations):
        expected_number = i + 1
        assert citation.number == expected_number, (
            f"Citation at index {i} should have number {expected_number}, "
            f"but has {citation.number}"
        )


@given(
    titles=st.lists(
        title_strategy,
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_all_citations_have_required_fields(titles: list):
    """
    **Feature: research-ai-assistant, Property 10: Citation Format Correctness**
    **Validates: Requirements 7.5, 7.6**
    
    For any citation in the final report, it SHALL have all required fields:
    number (positive int), title (non-empty string), and url (valid URL).
    """
    # Create citations with the generated titles
    citations = [
        Citation(
            number=i + 1,
            title=title,
            url=f"https://source{i + 1}.com/page"
        )
        for i, title in enumerate(titles)
    ]
    
    # Create a report
    report = FinalReport(
        summary="Research summary.",
        key_points=["Point 1"],
        comparison="Source comparison.",
        citations=citations,
        language="en"
    )
    
    # Verify each citation has all required fields with correct types
    for i, citation in enumerate(report.citations):
        # Check number field
        assert hasattr(citation, 'number'), f"Citation {i+1} must have 'number' field"
        assert isinstance(citation.number, int), f"Citation {i+1} number must be int"
        assert citation.number >= 1, f"Citation {i+1} number must be >= 1"
        
        # Check title field
        assert hasattr(citation, 'title'), f"Citation {i+1} must have 'title' field"
        assert isinstance(citation.title, str), f"Citation {i+1} title must be string"
        assert len(citation.title.strip()) > 0, f"Citation {i+1} title must not be empty"
        
        # Check url field
        assert hasattr(citation, 'url'), f"Citation {i+1} must have 'url' field"
        assert isinstance(citation.url, str), f"Citation {i+1} url must be string"
        assert citation.url.startswith(('http://', 'https://')), (
            f"Citation {i+1} url must start with http:// or https://"
        )


@given(
    num_citations=st.integers(min_value=3, max_value=10)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_citation_count_preserved_in_report(num_citations: int):
    """
    **Feature: research-ai-assistant, Property 10: Citation Format Correctness**
    **Validates: Requirements 7.5, 7.6**
    
    For any report with N citations, the citations list SHALL contain
    exactly N items, each with valid format.
    """
    # Create N citations
    citations = [
        Citation(
            number=i + 1,
            title=f"Article Title Number {i + 1}",
            url=f"https://website{i + 1}.org/content"
        )
        for i in range(num_citations)
    ]
    
    # Create report
    report = FinalReport(
        summary="Summary text.",
        key_points=["Point A", "Point B"],
        comparison="Comparison text.",
        citations=citations,
        language="en"
    )
    
    # Verify citation count is preserved
    assert len(report.citations) == num_citations, (
        f"Report should have {num_citations} citations, "
        f"but has {len(report.citations)}"
    )
    
    # Verify each citation is valid
    for citation in report.citations:
        assert citation.number >= 1
        assert len(citation.title.strip()) > 0
        assert citation.url.startswith(('http://', 'https://'))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
