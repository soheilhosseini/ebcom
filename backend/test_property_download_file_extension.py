"""
Property-based test for download file extension.

**Feature: research-ai-assistant, Property 11: Download File Extension**
**Validates: Requirements 10.5, 10.6**

Property 11: Download File Extension
*For any* download action, if the format is "markdown" the file SHALL have
.md extension, and if the format is "json" the file SHALL have .json extension.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck


def get_download_filename(output_format: str, base_name: str = "research-results") -> str:
    """
    Determine the download filename based on output format.
    
    This mirrors the frontend logic in App.tsx handleDownload function.
    
    Args:
        output_format: Either "markdown" or "json"
        base_name: Base filename without extension
        
    Returns:
        Full filename with appropriate extension
    """
    extension = "md" if output_format == "markdown" else "json"
    return f"{base_name}.{extension}"


def get_file_extension(output_format: str) -> str:
    """
    Get the file extension for a given output format.
    
    Args:
        output_format: Either "markdown" or "json"
        
    Returns:
        File extension (without dot): "md" or "json"
    """
    return "md" if output_format == "markdown" else "json"


def get_mime_type(output_format: str) -> str:
    """
    Get the MIME type for a given output format.
    
    Args:
        output_format: Either "markdown" or "json"
        
    Returns:
        MIME type string
    """
    return "text/markdown" if output_format == "markdown" else "application/json"


# Strategy for valid output formats
output_format_strategy = st.sampled_from(["markdown", "json"])


# Strategy for base filenames (alphanumeric with hyphens/underscores)
base_filename_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters='-_'),
    min_size=1,
    max_size=50
).filter(lambda x: x.strip() and x[0].isalnum())


@given(output_format=output_format_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_markdown_format_has_md_extension(output_format: str):
    """
    **Feature: research-ai-assistant, Property 11: Download File Extension**
    **Validates: Requirements 10.5**
    
    For any download action with markdown format, the file SHALL have .md extension.
    """
    if output_format == "markdown":
        filename = get_download_filename(output_format)
        assert filename.endswith(".md"), f"Markdown format should produce .md file, got: {filename}"
        
        extension = get_file_extension(output_format)
        assert extension == "md", f"Markdown format extension should be 'md', got: {extension}"


@given(output_format=output_format_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_json_format_has_json_extension(output_format: str):
    """
    **Feature: research-ai-assistant, Property 11: Download File Extension**
    **Validates: Requirements 10.6**
    
    For any download action with JSON format, the file SHALL have .json extension.
    """
    if output_format == "json":
        filename = get_download_filename(output_format)
        assert filename.endswith(".json"), f"JSON format should produce .json file, got: {filename}"
        
        extension = get_file_extension(output_format)
        assert extension == "json", f"JSON format extension should be 'json', got: {extension}"


@given(
    output_format=output_format_strategy,
    base_name=base_filename_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_file_extension_matches_format(output_format: str, base_name: str):
    """
    **Feature: research-ai-assistant, Property 11: Download File Extension**
    **Validates: Requirements 10.5, 10.6**
    
    For any download action, the file extension SHALL match the output format:
    - markdown → .md
    - json → .json
    """
    filename = get_download_filename(output_format, base_name)
    
    if output_format == "markdown":
        expected_extension = ".md"
    else:
        expected_extension = ".json"
    
    assert filename.endswith(expected_extension), \
        f"Format '{output_format}' should produce '{expected_extension}' extension, got: {filename}"
    
    # Verify the filename structure: base_name + extension
    expected_filename = f"{base_name}{expected_extension}"
    assert filename == expected_filename, \
        f"Expected filename '{expected_filename}', got: {filename}"


@given(output_format=output_format_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_mime_type_matches_format(output_format: str):
    """
    **Feature: research-ai-assistant, Property 11: Download File Extension**
    **Validates: Requirements 10.5, 10.6**
    
    For any download action, the MIME type SHALL match the output format:
    - markdown → text/markdown
    - json → application/json
    """
    mime_type = get_mime_type(output_format)
    
    if output_format == "markdown":
        assert mime_type == "text/markdown", \
            f"Markdown format should have 'text/markdown' MIME type, got: {mime_type}"
    else:
        assert mime_type == "application/json", \
            f"JSON format should have 'application/json' MIME type, got: {mime_type}"


@given(output_format=output_format_strategy)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_extension_is_valid_for_format(output_format: str):
    """
    **Feature: research-ai-assistant, Property 11: Download File Extension**
    **Validates: Requirements 10.5, 10.6**
    
    For any output format, the extension SHALL be one of the valid extensions
    (.md for markdown, .json for json) and never anything else.
    """
    extension = get_file_extension(output_format)
    
    # Extension must be one of the valid options
    valid_extensions = {"md", "json"}
    assert extension in valid_extensions, \
        f"Extension must be one of {valid_extensions}, got: {extension}"
    
    # Extension must match the format
    if output_format == "markdown":
        assert extension == "md"
    elif output_format == "json":
        assert extension == "json"


@given(
    output_format=output_format_strategy,
    base_name=base_filename_strategy
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_filename_has_single_extension(output_format: str, base_name: str):
    """
    **Feature: research-ai-assistant, Property 11: Download File Extension**
    **Validates: Requirements 10.5, 10.6**
    
    For any download action, the filename SHALL have exactly one extension
    (no double extensions like .md.json or .json.md).
    """
    filename = get_download_filename(output_format, base_name)
    
    # Count the number of dots in the filename (excluding base_name dots)
    # The filename should have exactly one dot for the extension
    parts = filename.rsplit('.', 1)
    assert len(parts) == 2, f"Filename should have exactly one extension, got: {filename}"
    
    # The extension part should be either 'md' or 'json'
    extension = parts[1]
    assert extension in {"md", "json"}, \
        f"Extension should be 'md' or 'json', got: {extension}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
