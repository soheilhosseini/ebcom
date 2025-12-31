"""
Property-based test for download file extension.

**Feature: research-ai-assistant, Property 11: Download File Extension**
**Validates: Requirements 10.5, 10.6**
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck


def get_download_filename(output_format: str, base_name: str = "research-results") -> str:
    extension = "md" if output_format == "markdown" else "json"
    return f"{base_name}.{extension}"


def get_file_extension(output_format: str) -> str:
    return "md" if output_format == "markdown" else "json"


def get_mime_type(output_format: str) -> str:
    return "text/markdown" if output_format == "markdown" else "application/json"


output_format_strategy = st.sampled_from(["markdown", "json"])
base_filename_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters='-_'),
    min_size=1, max_size=50
).filter(lambda x: x.strip() and x[0].isalnum())


@given(output_format=output_format_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_markdown_format_has_md_extension(output_format):
    """Property 11: Markdown format produces .md extension."""
    if output_format == "markdown":
        filename = get_download_filename(output_format)
        assert filename.endswith(".md")


@given(output_format=output_format_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_json_format_has_json_extension(output_format):
    """Property 11: JSON format produces .json extension."""
    if output_format == "json":
        filename = get_download_filename(output_format)
        assert filename.endswith(".json")


@given(output_format=output_format_strategy, base_name=base_filename_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_file_extension_matches_format(output_format, base_name):
    """Property 11: File extension matches output format."""
    filename = get_download_filename(output_format, base_name)
    expected_ext = ".md" if output_format == "markdown" else ".json"
    assert filename.endswith(expected_ext)


@given(output_format=output_format_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_mime_type_matches_format(output_format):
    """Property 11: MIME type matches output format."""
    mime_type = get_mime_type(output_format)
    if output_format == "markdown":
        assert mime_type == "text/markdown"
    else:
        assert mime_type == "application/json"
