"""
Property-based test for source count compliance.

**Feature: research-ai-assistant, Property 4: Source Count Compliance**
**Validates: Requirements 2.2**
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import patch
import asyncio

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.features.research.infrastructure.search import DuckDuckGoSearch
from src.features.research.domain.models import SearchResult


valid_source_count = st.integers(min_value=3, max_value=10)


@given(num_sources=valid_source_count)
@settings(max_examples=100)
def test_property_source_count_compliance(num_sources: int):
    """Property 4: WebSearcher requests exactly N results."""
    searcher = DuckDuckGoSearch()
    
    mock_results = [
        {"href": f"https://example{i}.com", "title": f"Title {i}", "body": f"Snippet {i}"}
        for i in range(num_sources)
    ]
    
    with patch.object(searcher._client, 'text', return_value=mock_results) as mock_text:
        results = asyncio.run(searcher.search("test query", num_sources))
        
        mock_text.assert_called_once()
        call_kwargs = mock_text.call_args
        assert call_kwargs.kwargs.get('max_results') == num_sources
        assert len(results) == num_sources


@given(num_sources=valid_source_count)
@settings(max_examples=100)
def test_property_source_count_returns_valid_results(num_sources: int):
    """Property 4: All results are valid SearchResult objects."""
    searcher = DuckDuckGoSearch()
    
    mock_results = [
        {"href": f"https://example{i}.com", "title": f"Title {i}", "body": f"Snippet {i}"}
        for i in range(num_sources)
    ]
    
    with patch.object(searcher._client, 'text', return_value=mock_results):
        results = asyncio.run(searcher.search("test query", num_sources))
        
        assert len(results) == num_sources
        for result in results:
            assert isinstance(result, SearchResult)
            assert result.url
            assert result.title
