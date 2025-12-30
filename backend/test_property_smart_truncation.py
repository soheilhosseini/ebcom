"""
Property-based test for smart truncation preservation.

**Feature: research-ai-assistant, Property 8: Smart Truncation Preservation**
**Validates: Requirements 5.3**

Property 8: Smart Truncation Preservation
*For any* content that undergoes smart truncation, the truncated result SHALL
preserve content from the beginning (intro) and end (conclusion) of the original text.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck

from extractor import ContentExtractor


# Strategy to generate a single paragraph with unique content
def paragraph_strategy(index: int):
    """Generate a paragraph with a unique prefix."""
    return st.text(
        alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S', 'Zs'), min_codepoint=32, max_codepoint=126),
        min_size=30,
        max_size=400
    ).filter(lambda x: x.strip()).map(lambda x: f"[Paragraph {index}] {x}")


@st.composite
def multi_paragraph_content(draw):
    """Generate multi-paragraph content with unique paragraphs."""
    num_paragraphs = draw(st.integers(min_value=3, max_value=15))
    paragraphs = []
    
    for i in range(num_paragraphs):
        para = draw(paragraph_strategy(i + 1))
        paragraphs.append(para)
    
    return '\n\n'.join(paragraphs)


@given(content=multi_paragraph_content())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property_smart_truncation_preserves_intro(content: str):
    """
    **Feature: research-ai-assistant, Property 8: Smart Truncation Preservation**
    **Validates: Requirements 5.3**
    
    For any content that undergoes smart truncation, the truncated result SHALL
    preserve content from the beginning (intro) of the original text.
    """
    extractor = ContentExtractor()
    
    # Get the first paragraph of the original content
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    assume(len(paragraphs) >= 3)  # Need at least 3 paragraphs for meaningful test
    
    first_paragraph = paragraphs[0]
    
    # Calculate total content length
    total_len = len(content)
    
    # Use a max_chars that forces truncation but gives enough budget for intro
    max_chars = max(len(first_paragraph) + 200, min(total_len // 2, 2000))
    assume(total_len > max_chars)  # Ensure we're actually truncating
    
    truncated = extractor.smart_truncate(content, max_chars=max_chars)
    
    # The truncated content should contain the first paragraph (intro)
    assert first_paragraph in truncated, (
        f"First paragraph not preserved in truncated content.\n"
        f"First paragraph: {first_paragraph[:100]}...\n"
        f"Truncated starts with: {truncated[:200]}..."
    )


@given(content=multi_paragraph_content())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property_smart_truncation_preserves_conclusion(content: str):
    """
    **Feature: research-ai-assistant, Property 8: Smart Truncation Preservation**
    **Validates: Requirements 5.3**
    
    For any content that undergoes smart truncation, the truncated result SHALL
    preserve content from the end (conclusion) of the original text.
    """
    extractor = ContentExtractor()
    
    # Get the last paragraph of the original content
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    assume(len(paragraphs) >= 3)  # Need at least 3 paragraphs for meaningful test
    
    last_paragraph = paragraphs[-1]
    
    # Calculate total content length
    total_len = len(content)
    
    # Use a max_chars that forces truncation but gives enough budget for conclusion
    max_chars = max(len(last_paragraph) + 200, min(total_len // 2, 2000))
    assume(total_len > max_chars)  # Ensure we're actually truncating
    
    truncated = extractor.smart_truncate(content, max_chars=max_chars)
    
    # The truncated content should contain the last paragraph (conclusion)
    assert last_paragraph in truncated, (
        f"Last paragraph not preserved in truncated content.\n"
        f"Last paragraph: {last_paragraph[:100]}...\n"
        f"Truncated ends with: ...{truncated[-200:]}"
    )


@given(content=multi_paragraph_content())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property_smart_truncation_respects_max_chars(content: str):
    """
    **Feature: research-ai-assistant, Property 8: Smart Truncation Preservation**
    **Validates: Requirements 5.3**
    
    For any content that undergoes smart truncation, the truncated result SHALL
    not exceed the specified max_chars limit.
    """
    extractor = ContentExtractor()
    
    # Generate a max_chars value that forces truncation
    max_chars = min(len(content) // 2, 2000)
    assume(max_chars >= 200)  # Need reasonable minimum
    
    truncated = extractor.smart_truncate(content, max_chars=max_chars)
    
    # The truncated content should not exceed max_chars
    assert len(truncated) <= max_chars, (
        f"Truncated content exceeds max_chars.\n"
        f"Max chars: {max_chars}, Actual: {len(truncated)}"
    )


@given(content=multi_paragraph_content())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_property_smart_truncation_preserves_both_ends(content: str):
    """
    **Feature: research-ai-assistant, Property 8: Smart Truncation Preservation**
    **Validates: Requirements 5.3**
    
    For any content that undergoes smart truncation with sufficient budget,
    the truncated result SHALL preserve content from BOTH the beginning (intro)
    AND the end (conclusion) of the original text.
    """
    extractor = ContentExtractor()
    
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    assume(len(paragraphs) >= 4)  # Need at least 4 paragraphs
    
    first_paragraph = paragraphs[0]
    last_paragraph = paragraphs[-1]
    
    # Calculate minimum budget needed for both intro and conclusion
    min_budget = len(first_paragraph) + len(last_paragraph) + 200
    max_chars = max(min_budget, min(len(content) // 2, 3000))
    
    # Ensure we're actually truncating
    assume(len(content) > max_chars)
    
    truncated = extractor.smart_truncate(content, max_chars=max_chars)
    
    # Both first and last paragraphs should be preserved
    assert first_paragraph in truncated, (
        f"First paragraph not preserved.\n"
        f"First: {first_paragraph[:80]}..."
    )
    assert last_paragraph in truncated, (
        f"Last paragraph not preserved.\n"
        f"Last: {last_paragraph[:80]}..."
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
