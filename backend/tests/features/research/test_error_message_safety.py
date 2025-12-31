"""
Property-based test for error message safety.

**Feature: research-ai-assistant, Property 12: Error Message Safety**
**Validates: Requirements 11.5**
"""

import pytest
import re
from hypothesis import given, strategies as st, settings

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.features.research.domain.exceptions import ResearchError


UNSAFE_PATTERNS = [
    r'Traceback \(most recent call last\)',
    r'File ".*\.py"',
    r'line \d+, in \w+',
    r'/home/\w+/',
    r'/usr/local/',
    r'C:\\Users\\',
    r'sk-[a-zA-Z0-9-]{20,}',
    r'api[_-]?key\s*[:=]\s*["\']?\w+',
    r'KeyError:',
    r'AttributeError:',
    r'TypeError:',
    r'OPENAI_API_KEY',
]


def contains_unsafe_content(message: str) -> tuple:
    for pattern in UNSAFE_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE | re.MULTILINE):
            return True, pattern
    return False, ""


safe_error_messages = st.sampled_from([
    "Unable to search. Please try again.",
    "Could not retrieve any sources. Please try a different topic.",
    "AI service unavailable. Please try again later.",
    "An unexpected error occurred. Please try again.",
    "Please enter a research topic",
])

unsafe_content_parts = st.sampled_from([
    'Traceback (most recent call last):',
    'File "/home/user/app/main.py", line 42',
    'KeyError: "api_key"',
    'sk-proj-abc123def456ghi789jkl012mno345pqr678',
    'OPENAI_API_KEY=sk-test123',
])


@given(message=safe_error_messages)
@settings(max_examples=100)
def test_property_research_error_messages_are_safe(message):
    """Property 12: ResearchError messages don't contain unsafe content."""
    error = ResearchError(message)
    is_unsafe, _ = contains_unsafe_content(error.message)
    assert not is_unsafe


@given(unsafe_part=unsafe_content_parts)
@settings(max_examples=100)
def test_property_unsafe_content_is_detected(unsafe_part):
    """Property 12: Safety check detects unsafe content."""
    is_unsafe, _ = contains_unsafe_content(unsafe_part)
    assert is_unsafe
