"""
Property-based tests for output formatting.

**Feature: research-ai-assistant, Property 5 & 6**
**Validates: Requirements 3.2, 3.3**
"""

import json
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.features.research.domain.models import FinalReport, Citation
from src.features.research.infrastructure.formatting import MarkdownJsonFormatter


# Strategies
text_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S', 'Z')),
    min_size=10, max_size=500
).filter(lambda x: x.strip())

citation_strategy = st.builds(
    Citation,
    number=st.integers(min_value=1, max_value=100),
    title=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    url=st.from_regex(r'https?://[a-z]+\.[a-z]{2,3}(/[a-z0-9]+)*', fullmatch=True)
)


@given(
    summary=text_strategy,
    key_points=st.lists(text_strategy, min_size=1, max_size=10),
    comparison=text_strategy,
    citations=st.lists(citation_strategy, min_size=1, max_size=10),
    language=st.sampled_from(["en", "fa"])
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_json_output_is_valid(summary, key_points, comparison, citations, language):
    """Property 5: JSON output is valid parseable JSON."""
    report = FinalReport(
        summary=summary, key_points=key_points, comparison=comparison,
        citations=citations, language=language
    )
    formatter = MarkdownJsonFormatter()
    output = formatter.format(report, "json")
    
    parsed = json.loads(output)
    assert "summary" in parsed
    assert "key_points" in parsed
    assert "comparison" in parsed
    assert "citations" in parsed


@given(
    summary=text_strategy,
    key_points=st.lists(text_strategy, min_size=1, max_size=10),
    comparison=text_strategy,
    citations=st.lists(citation_strategy, min_size=1, max_size=10),
    language=st.sampled_from(["en", "fa"])
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_markdown_contains_all_headers(summary, key_points, comparison, citations, language):
    """Property 6: Markdown contains all required headers."""
    report = FinalReport(
        summary=summary, key_points=key_points, comparison=comparison,
        citations=citations, language=language
    )
    formatter = MarkdownJsonFormatter()
    output = formatter.format(report, "markdown")
    
    for header in ["# Summary", "# Key Points", "# Comparison", "# Citations"]:
        assert header in output
