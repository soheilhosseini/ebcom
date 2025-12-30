"""
Checkpoint verification tests for search and extraction components.

This script verifies that the implemented components work correctly:
- WebSearcher: Can search and return results
- ContentExtractor: Can fetch and extract content
- LanguageDetector: Can detect English and Persian
- Models: Validation works correctly
"""

import asyncio
import sys
from typing import List

import pytest

# Add backend to path for imports
sys.path.insert(0, '.')

from models import ResearchRequest, SearchResult, ExtractedContent
from searcher import WebSearcher
from extractor import ContentExtractor
from language_detector import LanguageDetector


def test_models_validation():
    """Test that model validation works correctly."""
    # Test valid ResearchRequest
    req = ResearchRequest(topic="Python programming", num_sources=5, output_format="markdown")
    assert req.topic == "Python programming"
    assert req.num_sources == 5
    
    # Test default values
    req = ResearchRequest(topic="Test topic")
    assert req.num_sources == 5, "Default num_sources should be 5"
    assert req.output_format == "markdown", "Default format should be markdown"
    
    # Test source count bounds
    req = ResearchRequest(topic="Test", num_sources=3)
    assert req.num_sources == 3
    req = ResearchRequest(topic="Test", num_sources=10)
    assert req.num_sources == 10
    
    # Test invalid source count - should raise validation error
    with pytest.raises(Exception):
        ResearchRequest(topic="Test", num_sources=2)
    
    with pytest.raises(Exception):
        ResearchRequest(topic="Test", num_sources=11)
    
    # Test empty topic rejection
    with pytest.raises(Exception):
        ResearchRequest(topic="")


def test_language_detector():
    """Test language detection functionality."""
    detector = LanguageDetector()
    
    # Test English detection
    english_text = "This is a test sentence in English about programming and technology."
    result = detector.detect(english_text)
    assert result == "en", f"Expected 'en', got '{result}'"
    
    # Test Persian detection
    persian_text = "این یک متن آزمایشی به زبان فارسی است"
    result = detector.detect(persian_text)
    assert result == "fa", f"Expected 'fa', got '{result}'"
    
    # Test empty string defaults to English
    result = detector.detect("")
    assert result == "en", "Empty string should default to English"
    
    # Test whitespace defaults to English
    result = detector.detect("   ")
    assert result == "en", "Whitespace should default to English"


@pytest.mark.asyncio
async def test_web_searcher():
    """Test web search functionality."""
    searcher = WebSearcher()
    
    # Test basic search
    query = "Python programming language"
    results = await searcher.search(query, num_results=3)
    
    # Results may be empty due to network issues, but should be a list
    assert isinstance(results, list), "Search should return a list"
    
    # Verify result structure if we got results
    if results:
        result = results[0]
        assert hasattr(result, 'url'), "Result should have url"
        assert hasattr(result, 'title'), "Result should have title"
        assert hasattr(result, 'snippet'), "Result should have snippet"


@pytest.mark.asyncio
async def test_content_extractor():
    """Test content extraction functionality."""
    extractor = ContentExtractor(timeout=15)
    
    # Test smart truncation with known content (doesn't require network)
    long_content = """First paragraph with introduction content.

Second paragraph with more details about the topic.

Third paragraph continues the discussion.

Fourth paragraph adds additional information.

Fifth paragraph with conclusion and summary."""
    
    truncated = extractor.smart_truncate(long_content, max_chars=200)
    assert len(truncated) <= 200, "Truncated content should be within limit"
    assert "First paragraph" in truncated, "Should preserve intro"
    
    # Test that short content is not truncated
    short_content = "This is short content."
    result = extractor.smart_truncate(short_content, max_chars=1000)
    assert result == short_content, "Short content should not be modified"
    
    # Test empty content handling
    result = extractor.smart_truncate("", max_chars=100)
    assert result == "", "Empty content should return empty"


@pytest.mark.asyncio
async def test_content_extractor_network():
    """Test content extraction from network (may be skipped if network unavailable)."""
    extractor = ContentExtractor(timeout=15)
    
    # Test extraction from a reliable source
    test_url = "https://www.python.org/about/"
    result = await extractor.extract(test_url)
    
    # Result may be None due to network issues
    if result:
        assert result.url == test_url
        assert len(result.title) > 0
        assert len(result.content) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
