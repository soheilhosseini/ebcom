"""
Property-based test for source count compliance.

**Feature: research-ai-assistant, Property 4: Source Count Compliance**
**Validates: Requirements 2.2**

Property 4: Source Count Compliance
*For any* valid source count N (where 3 ≤ N ≤ 10), the Research_Agent SHALL
attempt to fetch and process exactly N sources from search results.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import MagicMock, patch

from searcher import WebSearcher
from models import SearchResult


# Strategy to generate valid source counts (3-10)
valid_source_count = st.integers(min_value=3, max_value=10)


@given(num_sources=valid_source_count)
@settings(max_examples=100)
def test_property_source_count_compliance(num_sources: int):
    """
    **Feature: research-ai-assistant, Property 4: Source Count Compliance**
    **Validates: Requirements 2.2**
    
    For any valid source count N (where 3 ≤ N ≤ 10), the WebSearcher SHALL
    request exactly N results from the search engine.
    """
    searcher = WebSearcher()
    
    # Mock the DDGS text method to capture the max_results parameter
    mock_results = [
        {"href": f"https://example{i}.com", "title": f"Title {i}", "body": f"Snippet {i}"}
        for i in range(num_sources)
    ]
    
    with patch.object(searcher._ddgs, 'text', return_value=mock_results) as mock_text:
        import asyncio
        results = asyncio.run(searcher.search("test query", num_sources))
        
        # Verify the searcher requested exactly num_sources results
        mock_text.assert_called_once()
        call_kwargs = mock_text.call_args
        
        # The max_results parameter should equal num_sources
        assert call_kwargs.kwargs.get('max_results') == num_sources, (
            f"Expected max_results={num_sources}, got {call_kwargs.kwargs.get('max_results')}"
        )
        
        # Verify we got the expected number of results back
        assert len(results) == num_sources, (
            f"Expected {num_sources} results, got {len(results)}"
        )


@given(num_sources=valid_source_count)
@settings(max_examples=100)
def test_property_source_count_returns_valid_results(num_sources: int):
    """
    **Feature: research-ai-assistant, Property 4: Source Count Compliance**
    **Validates: Requirements 2.2**
    
    For any valid source count N, when the search returns N results,
    all results SHALL be valid SearchResult objects with non-empty URLs.
    """
    searcher = WebSearcher()
    
    # Mock the DDGS text method to return exactly num_sources results
    mock_results = [
        {"href": f"https://example{i}.com", "title": f"Title {i}", "body": f"Snippet {i}"}
        for i in range(num_sources)
    ]
    
    with patch.object(searcher._ddgs, 'text', return_value=mock_results):
        import asyncio
        results = asyncio.run(searcher.search("test query", num_sources))
        
        # Verify all results are valid SearchResult objects
        assert len(results) == num_sources
        
        for i, result in enumerate(results):
            assert isinstance(result, SearchResult), (
                f"Result {i} is not a SearchResult: {type(result)}"
            )
            assert result.url, f"Result {i} has empty URL"
            assert result.title, f"Result {i} has empty title"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
