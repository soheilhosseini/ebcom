"""
Property-based test for JSON output validity.

**Feature: research-ai-assistant, Property 5: JSON Output Validity**
**Validates: Requirements 3.2**

Property 5: JSON Output Validity
*For any* research result formatted as JSON, the output SHALL be valid
parseable JSON containing all required fields (summary, key_points,
comparison, citations).
"""

import json
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
def test_property_json_output_is_valid_parseable_json(
    summary: str,
    key_points: list,
    comparison: str,
    citations: list,
    language: str
):
    """
    **Feature: research-ai-assistant, Property 5: JSON Output Validity**
    **Validates: Requirements 3.2**
    
    For any FinalReport formatted as JSON, the output SHALL be valid
    parseable JSON.
    """
    # Create a FinalReport
    report = FinalReport(
        summary=summary,
        key_points=key_points,
        comparison=comparison,
        citations=citations,
        language=language
    )
    
    # Format as JSON
    formatter = OutputFormatter()
    json_output = formatter.format(report, "json")
    
    # Verify the output is valid parseable JSON
    try:
        parsed = json.loads(json_output)
    except json.JSONDecodeError as e:
        pytest.fail(f"JSON output is not valid parseable JSON: {e}")
    
    # Verify parsed result is a dictionary
    assert isinstance(parsed, dict), "Parsed JSON should be a dictionary"


@given(
    summary=non_empty_text_strategy,
    key_points=key_points_strategy,
    comparison=non_empty_text_strategy,
    citations=citations_list_strategy,
    language=language_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_json_output_contains_all_required_fields(
    summary: str,
    key_points: list,
    comparison: str,
    citations: list,
    language: str
):
    """
    **Feature: research-ai-assistant, Property 5: JSON Output Validity**
    **Validates: Requirements 3.2**
    
    For any FinalReport formatted as JSON, the output SHALL contain
    all required fields: summary, key_points, comparison, citations.
    """
    # Create a FinalReport
    report = FinalReport(
        summary=summary,
        key_points=key_points,
        comparison=comparison,
        citations=citations,
        language=language
    )
    
    # Format as JSON
    formatter = OutputFormatter()
    json_output = formatter.format(report, "json")
    
    # Parse the JSON
    parsed = json.loads(json_output)
    
    # Verify all required fields are present
    required_fields = ["summary", "key_points", "comparison", "citations"]
    for field in required_fields:
        assert field in parsed, f"JSON output must contain '{field}' field"


@given(
    summary=non_empty_text_strategy,
    key_points=key_points_strategy,
    comparison=non_empty_text_strategy,
    citations=citations_list_strategy,
    language=language_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_json_output_preserves_content(
    summary: str,
    key_points: list,
    comparison: str,
    citations: list,
    language: str
):
    """
    **Feature: research-ai-assistant, Property 5: JSON Output Validity**
    **Validates: Requirements 3.2**
    
    For any FinalReport formatted as JSON, the content SHALL be
    preserved exactly in the output.
    """
    # Create a FinalReport
    report = FinalReport(
        summary=summary,
        key_points=key_points,
        comparison=comparison,
        citations=citations,
        language=language
    )
    
    # Format as JSON
    formatter = OutputFormatter()
    json_output = formatter.format(report, "json")
    
    # Parse the JSON
    parsed = json.loads(json_output)
    
    # Verify content is preserved
    assert parsed["summary"] == summary, "Summary content should be preserved"
    assert parsed["key_points"] == key_points, "Key points should be preserved"
    assert parsed["comparison"] == comparison, "Comparison content should be preserved"
    assert parsed["language"] == language, "Language should be preserved"
    
    # Verify citations are preserved
    assert len(parsed["citations"]) == len(citations), "Citation count should be preserved"
    for i, citation in enumerate(citations):
        assert parsed["citations"][i]["number"] == citation.number
        assert parsed["citations"][i]["title"] == citation.title
        assert parsed["citations"][i]["url"] == citation.url


@given(
    summary=non_empty_text_strategy,
    key_points=key_points_strategy,
    comparison=non_empty_text_strategy,
    citations=citations_list_strategy,
    language=language_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_json_output_field_types(
    summary: str,
    key_points: list,
    comparison: str,
    citations: list,
    language: str
):
    """
    **Feature: research-ai-assistant, Property 5: JSON Output Validity**
    **Validates: Requirements 3.2**
    
    For any FinalReport formatted as JSON, the fields SHALL have
    correct types: summary (string), key_points (array), comparison (string),
    citations (array of objects).
    """
    # Create a FinalReport
    report = FinalReport(
        summary=summary,
        key_points=key_points,
        comparison=comparison,
        citations=citations,
        language=language
    )
    
    # Format as JSON
    formatter = OutputFormatter()
    json_output = formatter.format(report, "json")
    
    # Parse the JSON
    parsed = json.loads(json_output)
    
    # Verify field types
    assert isinstance(parsed["summary"], str), "summary must be a string"
    assert isinstance(parsed["key_points"], list), "key_points must be an array"
    assert isinstance(parsed["comparison"], str), "comparison must be a string"
    assert isinstance(parsed["citations"], list), "citations must be an array"
    
    # Verify key_points contains strings
    for i, point in enumerate(parsed["key_points"]):
        assert isinstance(point, str), f"key_points[{i}] must be a string"
    
    # Verify citations are objects with required fields
    for i, citation in enumerate(parsed["citations"]):
        assert isinstance(citation, dict), f"citations[{i}] must be an object"
        assert "number" in citation, f"citations[{i}] must have 'number' field"
        assert "title" in citation, f"citations[{i}] must have 'title' field"
        assert "url" in citation, f"citations[{i}] must have 'url' field"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
