"""
Content extraction using Trafilatura.
"""

from typing import Optional, List

import httpx
import trafilatura

from src.shared.config import settings
from src.shared.utils import truncate_at_word_boundary
from src.features.research.domain.models import ExtractedContent
from src.features.research.constants import USER_AGENT, TRUNCATION_ELLIPSIS


class TrafilaturaExtractor:
    """Content extraction using httpx and trafilatura."""
    
    def __init__(self, timeout: int = None):
        self._timeout = timeout or settings.research.fetch_timeout_seconds
    
    async def extract(self, url: str) -> Optional[ExtractedContent]:
        """Extract main content from a webpage."""
        html = await self._fetch(url)
        if not html:
            return None
        
        content = self._extract_content(html)
        if not content:
            return None
        
        title = self._extract_title(html, fallback=url)
        return ExtractedContent(url=url, title=title, content=content)
    
    def truncate(self, content: str, max_chars: int = None) -> str:
        """Smart truncation preserving intro and conclusion."""
        max_chars = max_chars or settings.research.max_content_chars
        
        if not content or len(content) <= max_chars:
            return content or ""
        
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        
        if len(paragraphs) <= 1:
            return truncate_at_word_boundary(content, max_chars)
        
        return self._truncate_preserving_structure(paragraphs, max_chars)
    
    async def _fetch(self, url: str) -> Optional[str]:
        """Fetch webpage HTML."""
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout),
                follow_redirects=True,
                headers={"User-Agent": USER_AGENT}
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except Exception:
            return None
    
    def _extract_content(self, html: str) -> Optional[str]:
        """Extract main content from HTML."""
        try:
            return trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
        except Exception:
            return None
    
    def _extract_title(self, html: str, fallback: str) -> str:
        """Extract page title from HTML."""
        try:
            metadata = trafilatura.extract_metadata(html)
            if metadata and metadata.title:
                return metadata.title
        except Exception:
            pass
        return fallback
    
    def _truncate_preserving_structure(
        self,
        paragraphs: List[str],
        max_chars: int
    ) -> str:
        """Truncate while keeping intro and conclusion."""
        first = paragraphs[0]
        last = paragraphs[-1]
        separator = "\n\n"
        ellipsis = TRUNCATION_ELLIPSIS
        
        min_required = len(first) + len(last) + len(separator)
        if min_required > max_chars:
            return truncate_at_word_boundary(first, max_chars)
        
        # Calculate budget for middle content
        overhead = len(separator) * 2 + len(ellipsis) + len(separator)
        middle_budget = max_chars - len(first) - len(last) - overhead
        
        # Fit middle paragraphs
        middle = paragraphs[1:-1] if len(paragraphs) > 2 else []
        included = []
        used = 0
        
        for para in middle:
            para_len = len(para) + len(separator)
            if used + para_len <= middle_budget:
                included.append(para)
                used += para_len
            else:
                break
        
        # Assemble result
        parts = [first]
        if included:
            parts.extend(included)
        if len(included) < len(middle):
            parts.append(ellipsis)
        parts.append(last)
        
        return separator.join(parts)
