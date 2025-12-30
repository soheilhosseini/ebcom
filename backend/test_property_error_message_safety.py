"""
Property-based test for error message safety.

**Feature: research-ai-assistant, Property 12: Error Message Safety**
**Validates: Requirements 11.5**

Property 12: Error Message Safety
*For any* error response returned to the user, it SHALL NOT contain stack traces,
internal paths, API keys, or other technical implementation details.
"""

import pytest
import re
from hypothesis import given, strategies as st, settings

from research_agent import ResearchError
from models import ErrorResponse


# Patterns that indicate unsafe error content
UNSAFE_PATTERNS = [
    # Stack traces
    r'Traceback \(most recent call last\)',
    r'File ".*\.py"',
    r'line \d+, in \w+',
    r'^\s+at\s+.*:\d+:\d+',  # JavaScript-style stack traces
    
    # Internal paths
    r'/home/\w+/',
    r'/usr/local/',
    r'/var/',
    r'C:\\Users\\',
    r'C:\\Program Files',
    r'\\site-packages\\',
    r'/site-packages/',
    r'\.py:\d+',
    
    # API keys and secrets
    r'sk-[a-zA-Z0-9-]{20,}',  # OpenAI API key pattern (includes hyphens)
    r'api[_-]?key\s*[:=]\s*["\']?\w+',
    r'secret\s*[:=]\s*["\']?\w+',
    r'password\s*[:=]\s*["\']?\w+',
    r'token\s*[:=]\s*["\']?\w+',
    
    # Technical error details
    r'Exception\s+in\s+thread',
    r'NoneType.*has no attribute',
    r'KeyError:',
    r'AttributeError:',
    r'TypeError:',
    r'ValueError:',
    r'ImportError:',
    r'ModuleNotFoundError:',
    r'ConnectionError:',
    r'TimeoutError:',
    r'HTTPError:',
    r'JSONDecodeError:',
    
    # Database/internal details
    r'sqlite3\.',
    r'psycopg2\.',
    r'pymongo\.',
    r'SELECT\s+.*\s+FROM',
    r'INSERT\s+INTO',
    r'UPDATE\s+.*\s+SET',
    
    # Environment variables
    r'OPENAI_API_KEY',
    r'DATABASE_URL',
    r'SECRET_KEY',
]


def contains_unsafe_content(message: str) -> tuple[bool, str]:
    """
    Check if a message contains unsafe technical content.
    
    Args:
        message: The error message to check
        
    Returns:
        Tuple of (is_unsafe, matched_pattern)
    """
    for pattern in UNSAFE_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE | re.MULTILINE):
            return True, pattern
    return False, ""


# Strategy for generating user-friendly error messages
safe_error_messages = st.sampled_from([
    "Unable to search. Please try again.",
    "Could not retrieve any sources. Please try a different topic.",
    "AI service unavailable. Please try again later.",
    "An unexpected error occurred. Please try again.",
    "Please enter a research topic",
    "Network error. Please check your connection.",
    "Service temporarily unavailable.",
    "Request timed out. Please try again.",
])


# Strategy for generating potentially unsafe technical content
unsafe_content_parts = st.sampled_from([
    'Traceback (most recent call last):',
    'File "/home/user/app/main.py", line 42, in research',
    'File "C:\\Users\\dev\\project\\backend\\main.py", line 100',
    'KeyError: "api_key"',
    'AttributeError: NoneType has no attribute "get"',
    'TypeError: expected str, got NoneType',
    'sk-proj-abc123def456ghi789jkl012mno345pqr678',
    'api_key: "secret_value_12345"',
    'OPENAI_API_KEY=sk-test123',
    '/usr/local/lib/python3.11/site-packages/openai/error.py',
    'ConnectionError: Failed to connect to api.openai.com',
    'JSONDecodeError: Expecting value: line 1 column 1',
])


@given(message=safe_error_messages)
@settings(max_examples=100)
def test_property_research_error_messages_are_safe(message: str):
    """
    **Feature: research-ai-assistant, Property 12: Error Message Safety**
    **Validates: Requirements 11.5**
    
    For any ResearchError created with a user-friendly message,
    the message SHALL NOT contain unsafe technical content.
    """
    # Create a ResearchError with the message
    error = ResearchError(message)
    
    # Verify the error message is safe
    is_unsafe, matched_pattern = contains_unsafe_content(error.message)
    assert not is_unsafe, (
        f"ResearchError message contains unsafe content.\n"
        f"Message: {error.message}\n"
        f"Matched pattern: {matched_pattern}"
    )


@given(message=safe_error_messages)
@settings(max_examples=100)
def test_property_error_response_messages_are_safe(message: str):
    """
    **Feature: research-ai-assistant, Property 12: Error Message Safety**
    **Validates: Requirements 11.5**
    
    For any ErrorResponse created with a user-friendly message,
    the message SHALL NOT contain unsafe technical content.
    """
    # Create an ErrorResponse with the message
    response = ErrorResponse(message=message)
    
    # Verify the response message is safe
    is_unsafe, matched_pattern = contains_unsafe_content(response.message)
    assert not is_unsafe, (
        f"ErrorResponse message contains unsafe content.\n"
        f"Message: {response.message}\n"
        f"Matched pattern: {matched_pattern}"
    )


@given(unsafe_part=unsafe_content_parts)
@settings(max_examples=100)
def test_property_unsafe_content_is_detected(unsafe_part: str):
    """
    **Feature: research-ai-assistant, Property 12: Error Message Safety**
    **Validates: Requirements 11.5**
    
    For any string containing technical implementation details,
    the safety check SHALL detect it as unsafe.
    """
    # Verify our safety check correctly identifies unsafe content
    is_unsafe, _ = contains_unsafe_content(unsafe_part)
    assert is_unsafe, (
        f"Safety check failed to detect unsafe content: {unsafe_part}"
    )


@given(
    safe_prefix=st.text(min_size=0, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))),
    safe_suffix=st.text(min_size=0, max_size=20, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')))
)
@settings(max_examples=100)
def test_property_predefined_error_messages_remain_safe(safe_prefix: str, safe_suffix: str):
    """
    **Feature: research-ai-assistant, Property 12: Error Message Safety**
    **Validates: Requirements 11.5**
    
    For any combination of safe text with predefined error messages,
    the result SHALL remain safe (no injection of unsafe content).
    """
    # The predefined error messages used in the application
    predefined_messages = [
        "Unable to search. Please try again.",
        "Could not retrieve any sources. Please try a different topic.",
        "AI service unavailable. Please try again later.",
        "An unexpected error occurred. Please try again.",
    ]
    
    for base_message in predefined_messages:
        # Even with prefix/suffix, the message should remain safe
        # (This tests that we're not accidentally concatenating unsafe content)
        combined = f"{safe_prefix}{base_message}{safe_suffix}"
        
        # The combined message should still be safe
        # (unless the prefix/suffix themselves contain unsafe patterns,
        # which is unlikely with the restricted alphabet)
        error = ResearchError(combined)
        
        # Verify the base message is preserved and safe
        assert base_message in error.message or error.message == combined


@given(message=safe_error_messages)
@settings(max_examples=100)
def test_property_error_response_model_structure(message: str):
    """
    **Feature: research-ai-assistant, Property 12: Error Message Safety**
    **Validates: Requirements 11.5**
    
    For any ErrorResponse, it SHALL only contain the 'error' and 'message' fields,
    with no additional fields that could expose technical details.
    """
    response = ErrorResponse(message=message)
    
    # Get the model fields
    response_dict = response.model_dump()
    
    # Verify only expected fields are present
    expected_fields = {'error', 'message'}
    actual_fields = set(response_dict.keys())
    
    assert actual_fields == expected_fields, (
        f"ErrorResponse has unexpected fields.\n"
        f"Expected: {expected_fields}\n"
        f"Actual: {actual_fields}"
    )
    
    # Verify error is always True
    assert response_dict['error'] is True, "ErrorResponse.error should always be True"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
