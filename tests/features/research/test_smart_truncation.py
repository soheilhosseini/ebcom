"""
Property-based test for smart truncation preservation.

**Feature: research-ai-assistant, Property 8: Smart Truncation Preservation**
**Validates: Requirements 5.3**
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.features.research.infrastructure.extraction import TrafilaturaExtractor


def paragraph_strategy(index: int):
    return st.text(
        alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S', 'Zs'), min_codepoint=32, max_codepoint=126),
        min_size=30, max_size=400
    ).filter(lambda x: x.strip()).map(lambda x: f"[Paragraph {index}] {x}")


@st.composite
def multi_paragraph_content(draw):
    num_paragraphs = draw(st.integers(min_value=3, max_value=15))
    paragraphs = [draw(paragraph_strategy(i + 1)) for i in range(num_paragraphs)]
    return '\n\n'.join(paragraphs)


@given(content=multi_paragraph_content())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_smart_truncation_preserves_intro(content: str):
    """Property 8: Truncation preserves intro."""
    extractor = TrafilaturaExtractor()
    
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    assume(len(paragraphs) >= 3)
    
    first_paragraph = paragraphs[0]
    total_len = len(content)
    max_chars = max(len(first_paragraph) + 200, min(total_len // 2, 2000))
    assume(total_len > max_chars)
    
    truncated = extractor.truncate(content, max_chars=max_chars)
    assert first_paragraph in truncated


@given(content=multi_paragraph_content())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_smart_truncation_preserves_conclusion(content: str):
    """Property 8: Truncation preserves conclusion."""
    extractor = TrafilaturaExtractor()
    
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    assume(len(paragraphs) >= 3)
    
    last_paragraph = paragraphs[-1]
    total_len = len(content)
    max_chars = max(len(last_paragraph) + 200, min(total_len // 2, 2000))
    assume(total_len > max_chars)
    
    truncated = extractor.truncate(content, max_chars=max_chars)
    assert last_paragraph in truncated


@given(content=multi_paragraph_content())
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_property_smart_truncation_respects_max_chars(content: str):
    """Property 8: Truncation respects max_chars limit."""
    extractor = TrafilaturaExtractor()
    
    max_chars = min(len(content) // 2, 2000)
    assume(max_chars >= 200)
    
    truncated = extractor.truncate(content, max_chars=max_chars)
    assert len(truncated) <= max_chars
