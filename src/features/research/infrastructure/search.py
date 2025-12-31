"""
DuckDuckGo search implementation.
"""

from typing import List
from duckduckgo_search import DDGS

from src.features.research.domain.models import SearchResult


class DuckDuckGoSearch:
    """Web search using DuckDuckGo (no API key required)."""
    
    def __init__(self):
        self._client = DDGS()
    
    async def search(self, query: str, num_results: int) -> List[SearchResult]:
        """Search the web for relevant sources."""
        try:
            raw_results = self._client.text(query, max_results=num_results)
            return [
                SearchResult(
                    url=item.get("href", ""),
                    title=item.get("title", ""),
                    snippet=item.get("body", "")
                )
                for item in raw_results
                if item.get("href")
            ]
        except Exception:
            return []
