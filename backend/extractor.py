"""
Content extraction module for the Research AI Assistant.

This module handles fetching webpages and extracting main content
using trafilatura. It implements smart truncation to preserve
intro and conclusion sections.
"""

import asyncio
from typing import Optional

import httpx
import trafilatura

from models import ExtractedContent


class ContentExtractor:
    """
    Extracts main content from webpages.
    
    Uses httpx for async HTTP requests and trafilatura for content extraction.
    Implements smart truncation to preserve document structure.
    """
    
    DEFAULT_TIMEOUT = 15  # seconds
    DEFAULT_MAX_CHARS = 8000  # approximately 2000 tokens
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the content extractor.
        
        Args:
            timeout: Timeout in seconds for HTTP requests (default 15)
        """
        self.timeout = timeout
    
    async def extract(self, url: str, timeout: Optional[int] = None) -> Optional[ExtractedContent]:
        """
        Fetch webpage and extract main content.
        
        Args:
            url: URL to fetch
            timeout: Optional timeout override in seconds
            
        Returns:
            ExtractedContent or None if fetch/extraction failed
        """
        request_timeout = timeout if timeout is not None else self.timeout
        
        try:
            # Fetch the webpage
            html = await self._fetch_page(url, request_timeout)
            if html is None:
                return None
            
            # Extract content using trafilatura
            content = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
            
            if not content:
                return None
            
            # Extract title
            title = self._extract_title(html, url)
            
            return ExtractedContent(
                url=url,
                title=title,
                content=content
            )
            
        except Exception:
            # Handle all failures silently as per requirements 5.4, 5.5
            return None
    
    async def _fetch_page(self, url: str, timeout: int) -> Optional[str]:
        """
        Fetch a webpage with timeout.
        
        Args:
            url: URL to fetch
            timeout: Timeout in seconds
            
        Returns:
            HTML content as string or None if failed
        """
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(timeout),
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError):
            # Silently handle fetch failures
            return None
        except Exception:
            # Catch any other unexpected errors
            return None
    
    def _extract_title(self, html: str, fallback_url: str) -> str:
        """
        Extract title from HTML or use URL as fallback.
        
        Args:
            html: HTML content
            fallback_url: URL to use if title extraction fails
            
        Returns:
            Extracted title or URL as fallback
        """
        try:
            metadata = trafilatura.extract_metadata(html)
            if metadata and metadata.title:
                return metadata.title
        except Exception:
            pass
        
        # Fallback to URL
        return fallback_url
    
    def smart_truncate(self, content: str, max_chars: int = DEFAULT_MAX_CHARS) -> str:
        """
        Smart truncation: preserves intro + key sections + conclusion.
        
        This method ensures that the beginning (intro) and end (conclusion)
        of the content are preserved, with middle sections included as space allows.
        
        Args:
            content: Full extracted content
            max_chars: Maximum characters to keep (default ~2000 tokens)
            
        Returns:
            Truncated content preserving structure
        """
        if not content:
            return ""
        
        # If content is already within limits, return as-is
        if len(content) <= max_chars:
            return content
        
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            # Fallback: simple truncation if no paragraph structure
            return self._simple_truncate(content, max_chars)
        
        if len(paragraphs) == 1:
            # Single paragraph: truncate with ellipsis
            return self._simple_truncate(paragraphs[0], max_chars)
        
        # PRIORITY: Always include first and last paragraphs (intro and conclusion)
        first_para = paragraphs[0]
        last_para = paragraphs[-1]
        
        # Calculate space needed for intro and conclusion
        intro_len = len(first_para)
        conclusion_len = len(last_para)
        separator_len = 4  # "\n\n" between sections
        ellipsis_len = 7  # "[...]" + "\n\n"
        
        # Check if we can fit at least intro and conclusion
        min_required = intro_len + conclusion_len + separator_len
        
        if min_required > max_chars:
            # Not enough space for both - prioritize intro, truncate conclusion
            if intro_len + ellipsis_len + 50 <= max_chars:
                # Fit intro and truncated conclusion
                remaining = max_chars - intro_len - separator_len - ellipsis_len - separator_len
                if remaining > 20:
                    truncated_conclusion = self._simple_truncate(last_para, remaining)
                    return first_para + "\n\n[...]\n\n" + truncated_conclusion
                else:
                    return self._simple_truncate(first_para, max_chars)
            else:
                return self._simple_truncate(first_para, max_chars)
        
        # We can fit both intro and conclusion - now add middle content if space allows
        remaining_budget = max_chars - intro_len - conclusion_len - separator_len - ellipsis_len - separator_len
        
        # Get middle paragraphs (excluding first and last)
        middle_paragraphs = paragraphs[1:-1] if len(paragraphs) > 2 else []
        
        # Build middle section from remaining paragraphs
        middle_parts = []
        middle_chars = 0
        
        for para in middle_paragraphs:
            para_len = len(para) + separator_len
            if middle_chars + para_len <= remaining_budget:
                middle_parts.append(para)
                middle_chars += para_len
            else:
                break
        
        # Combine sections
        result_parts = [first_para]
        
        if middle_parts:
            result_parts.extend(middle_parts)
            # Check if we skipped any middle content
            if len(middle_parts) < len(middle_paragraphs):
                result_parts.append("[...]")
        elif middle_paragraphs:
            # We have middle paragraphs but couldn't fit any
            result_parts.append("[...]")
        
        result_parts.append(last_para)
        
        return '\n\n'.join(result_parts)
    
    def _simple_truncate(self, text: str, max_chars: int) -> str:
        """
        Simple truncation with ellipsis at word boundary.
        
        Args:
            text: Text to truncate
            max_chars: Maximum characters
            
        Returns:
            Truncated text with ellipsis if needed
        """
        if len(text) <= max_chars:
            return text
        
        # Find last space before limit to avoid cutting words
        truncate_at = text.rfind(' ', 0, max_chars - 3)
        if truncate_at == -1:
            truncate_at = max_chars - 3
        
        return text[:truncate_at] + "..."
