"""
Property-based test for input validation.

**Feature: research-ai-assistant, Property 3: Empty Input Rejection**
**Validates: Requirements 1.4**

Property 3: Empty Input Rejection
*For any* string composed entirely of whitespace characters (including empty string),
the validation SHALL reject it and prevent submission.
"""

import pytest
from hypothesis import given, strategies as st, settings
from pydantic import ValidationError

from models import ResearchRequest


# Strategy to generate whitespace-only strings
whitespace_chars = st.sampled_from([' ', '\t', '\n', '\r', '\f', '\v'])
whitespace_strings = st.text(alphabet=whitespace_chars, min_size=0, max_size=100)


@given(whitespace_input=whitespace_strings)
@settings(max_examples=100)
def test_property_empty_input_rejection(whitespace_input: str):
    """
    **Feature: research-ai-assistant, Property 3: Empty Input Rejection**
    **Validates: Requirements 1.4**
    
    For any string composed entirely of whitespace characters (including empty string),
    the validation SHALL reject it and prevent submission.
    """
    # Whitespace-only strings should be rejected by validation
    with pytest.raises(ValidationError):
        ResearchRequest(topic=whitespace_input)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
