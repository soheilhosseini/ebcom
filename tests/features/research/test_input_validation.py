"""
Property-based test for input validation.

**Feature: research-ai-assistant, Property 3: Empty Input Rejection**
**Validates: Requirements 1.4**
"""

import pytest
from hypothesis import given, strategies as st, settings
from pydantic import ValidationError

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.features.research.domain.models import ResearchRequest


whitespace_chars = st.sampled_from([' ', '\t', '\n', '\r', '\f', '\v'])
whitespace_strings = st.text(alphabet=whitespace_chars, min_size=0, max_size=100)


@given(whitespace_input=whitespace_strings)
@settings(max_examples=100)
def test_property_empty_input_rejection(whitespace_input: str):
    """Property 3: Whitespace-only strings rejected."""
    with pytest.raises(ValidationError):
        ResearchRequest(topic=whitespace_input)
