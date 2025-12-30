"""
Property-based test for Markdown output structure.

**Feature: research-ai-assistant, Property 6: Markdown Output Structure**
**Validates: Requirements 3.3**

Property 6: Markdown Output Structure
*For any* research result formatted as Markdown, the output SHALL contain
properly formatted sections with headers for Summary, Key Points, Comparison,
and Citations.
"""

import re
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from models import FinalReport, Citation
from formatter import OutputFormatter


# Strategy to generate non-empty strings for report content
non_empty_text_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S', 'Z')),
    min_size=10,
    max_size=500
).filter(lambda x: x.strip())


# Strategy to generate valid citations
citation_strategy = st.builds(
    Citation,
    number=st.integers(min_value=1, max_value=100),
    title=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    url=st.from_regex(r'https?://[a-z]+\.[a-z]{2,3}(/[a-z0-9]+)*', fullmatch=True)
)


# Strategy to generate a list of citations (at least 1)
citations_list_strategy = st.lists(
    citation_strategy,
    min_size=1,
    max_size=10
)


# Strategy to generate key points (list of non-empty strings)
key_points_strategy = st.lists(
    non_empty_text_strategy,
    min_size=1,
    max_size=10
)


# Strategy to generate language codes
language_strategy = st.sampled_from(["en", "fa"])


@given(
    summary=non_empty_text_strategy,
    key_points=key_points_strategy,
    comparison=non_empty_text_strategy,
    citations=citations_list_strategy,
    language=language_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_markdown_contains_all_required_headers(
    summary: str,
    key_points: list,
    comparison: str,
    citations: list,
    language: str
):
    """
    **Feature: research-ai-assistant, Property 6: Markdown Output Structure**
    **Validates: Requirements 3.3**
    
    For any FinalReport formatted as Markdown, the output SHALL contain
    properly formatted headers for Summary, Key Points, Comparison, and Citations.
    """
    # Create a FinalReport
    report = FinalReport(
        summary=summary,
        key_points=key_points,
        comparison=comparison,
        citations=citations,
        language=language
    )
    
    # Format as Markdown
    formatter = OutputFormatter()
    markdown_output = formatter.format(report, "markdown")
    
    # Verify all required headers are present (using # for h1 headers)
    required_headers = ["# Summary", "# Key Points", "# Comparison", "# Citations"]
    for header in required_headers:
        assert header in markdown_output, f"Markdown output must contain '{header}' header"


@given(
    summary=non_empty_text_strategy,
    key_points=key_points_strategy,
    comparison=non_empty_text_strategy,
    citations=citations_list_strategy,
    language=language_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_markdown_summary_section_contains_content(
    summary: str,
    key_points: list,
    comparison: str,
    citations: list,
    language: str
):
    """
    **Feature: research-ai-assistant, Property 6: Markdown Output Structure**
    **Validates: Requirements 3.3**
    
    For any FinalReport formatted as Markdown, the Summary section SHALL
    contain the summary content.
    """
    # Create a FinalReport
    report = FinalReport(
        summary=summary,
        key_points=key_points,
        comparison=comparison,
        citations=citations,
        language=language
    )
    
    # Format as Markdown
    formatter = OutputFormatter()
    markdown_output = formatter.format(report, "markdown")
    
    # Verify summary content is present after the Summary header
    assert summary in markdown_output, "Summary content must be present in Markdown output"


@given(
    summary=non_empty_text_strategy,
    key_points=key_points_strategy,
    comparison=non_empty_text_strategy,
    citations=citations_list_strategy,
    language=language_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_markdown_key_points_formatted_as_list(
    summary: str,
    key_points: list,
    comparison: str,
    citations: list,
    language: str
):
    """
    **Feature: research-ai-assistant, Property 6: Markdown Output Structure**
    **Validates: Requirements 3.3**
    
    For any FinalReport formatted as Markdown, the Key Points section SHALL
    contain all key points formatted as a bullet list.
    """
    # Create a FinalReport
    report = FinalReport(
        summary=summary,
        key_points=key_points,
        comparison=comparison,
        citations=citations,
        language=language
    )
    
    # Format as Markdown
    formatter = OutputFormatter()
    markdown_output = formatter.format(report, "markdown")
    
    # Verify each key point is present as a bullet item
    for point in key_points:
        bullet_item = f"- {point}"
        assert bullet_item in markdown_output, f"Key point '{point}' must be formatted as bullet item"


@given(
    summary=non_empty_text_strategy,
    key_points=key_points_strategy,
    comparison=non_empty_text_strategy,
    citations=citations_list_strategy,
    language=language_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_markdown_comparison_section_contains_content(
    summary: str,
    key_points: list,
    comparison: str,
    citations: list,
    language: str
):
    """
    **Feature: research-ai-assistant, Property 6: Markdown Output Structure**
    **Validates: Requirements 3.3**
    
    For any FinalReport formatted as Markdown, the Comparison section SHALL
    contain the comparison content.
    """
    # Create a FinalReport
    report = FinalReport(
        summary=summary,
        key_points=key_points,
        comparison=comparison,
        citations=citations,
        language=language
    )
    
    # Format as Markdown
    formatter = OutputFormatter()
    markdown_output = formatter.format(report, "markdown")
    
    # Verify comparison content is present
    assert comparison in markdown_output, "Comparison content must be present in Markdown output"


@given(
    summary=non_empty_text_strategy,
    key_points=key_points_strategy,
    comparison=non_empty_text_strategy,
    citations=citations_list_strategy,
    language=language_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_markdown_citations_formatted_correctly(
    summary: str,
    key_points: list,
    comparison: str,
    citations: list,
    language: str
):
    """
    **Feature: research-ai-assistant, Property 6: Markdown Output Structure**
    **Validates: Requirements 3.3**
    
    For any FinalReport formatted as Markdown, the Citations section SHALL
    contain all citations with number, title, and URL.
    """
    # Create a FinalReport
    report = FinalReport(
        summary=summary,
        key_points=key_points,
        comparison=comparison,
        citations=citations,
        language=language
    )
    
    # Format as Markdown
    formatter = OutputFormatter()
    markdown_output = formatter.format(report, "markdown")
    
    # Verify each citation is present with proper format: [N] Title - URL
    for citation in citations:
        citation_format = f"[{citation.number}] {citation.title} - {citation.url}"
        assert citation_format in markdown_output, \
            f"Citation must be formatted as '[{citation.number}] {citation.title} - {citation.url}'"


@given(
    summary=non_empty_text_strategy,
    key_points=key_points_strategy,
    comparison=non_empty_text_strategy,
    citations=citations_list_strategy,
    language=language_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_markdown_sections_in_correct_order(
    summary: str,
    key_points: list,
    comparison: str,
    citations: list,
    language: str
):
    """
    **Feature: research-ai-assistant, Property 6: Markdown Output Structure**
    **Validates: Requirements 3.3**
    
    For any FinalReport formatted as Markdown, the sections SHALL appear
    in the correct order: Summary, Key Points, Comparison, Citations.
    """
    # Create a FinalReport
    report = FinalReport(
        summary=summary,
        key_points=key_points,
        comparison=comparison,
        citations=citations,
        language=language
    )
    
    # Format as Markdown
    formatter = OutputFormatter()
    markdown_output = formatter.format(report, "markdown")
    
    # Find positions of each header
    summary_pos = markdown_output.find("# Summary")
    key_points_pos = markdown_output.find("# Key Points")
    comparison_pos = markdown_output.find("# Comparison")
    citations_pos = markdown_output.find("# Citations")
    
    # Verify all headers are found
    assert summary_pos != -1, "Summary header must be present"
    assert key_points_pos != -1, "Key Points header must be present"
    assert comparison_pos != -1, "Comparison header must be present"
    assert citations_pos != -1, "Citations header must be present"
    
    # Verify correct order
    assert summary_pos < key_points_pos, "Summary must come before Key Points"
    assert key_points_pos < comparison_pos, "Key Points must come before Comparison"
    assert comparison_pos < citations_pos, "Comparison must come before Citations"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
