"""
Web search component using DuckDuckGo.

This module provides web search functionality for the Research AI Assistant
using the DuckDuckGo search engine (no API key required).
"""

from typing import List
from duckduckgo_search import DDGS
from models import SearchResult


class WebSearcher:
    """
    Web searcher using DuckDuckGo search.
    
    Provides free web search functionality without requiring API keys.
    """
    
    def __init__(self):
        """Initialize the web searcher."""
        self._ddgs = DDGS()
    
    async def search(self, query: str, num_results: int) -> List[SearchResult]:
        """
        Search the web for relevant sources.
        
        Args:
            query: Search query (research topic)
            num_results: Number of results to return (3-10)
            
        Returns:
            List of SearchResult with url, title, snippet
        """
        results: List[SearchResult] = []
        
        try:
            # DuckDuckGo text search returns results with href, title, body
            search_results = self._ddgs.text(
                query,
                max_results=num_results
            )
            
            for item in search_results:
                result = SearchResult(
                    url=item.get("href", ""),
                    title=item.get("title", ""),
                    snippet=item.get("body", "")
                )
                # Only add results with valid URLs
                if result.url:
                    results.append(result)
                    
        except Exception:
            # Return empty list on search failure
            # The Research Agent will handle this gracefully
            pass
        
        return results
