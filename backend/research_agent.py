"""
Research Agent orchestrator for the Research AI Assistant.

This module provides the main ResearchAgent class that orchestrates
all components: search, extraction, summarization, reasoning, and formatting.
It handles progress callbacks for SSE events and graceful error handling.
"""

import asyncio
from typing import Callable, Optional, Awaitable

from models import (
    ResearchRequest,
    SearchResult,
    SourceSummary,
    FinalReport,
    ProgressEvent
)
from searcher import WebSearcher
from extractor import ContentExtractor
from summarizer import Summarizer
from reasoning_chain import ReasoningChain
from formatter import OutputFormatter
from language_detector import LanguageDetector


class ResearchAgent:
    """
    Main orchestrator for the research workflow.
    
    Coordinates all components to execute the full research pipeline:
    1. Detect input language
    2. Search web for sources
    3. Extract content from sources
    4. Summarize each source
    5. Generate final report with reasoning
    6. Format output as JSON or Markdown
    
    Handles errors gracefully by skipping failed sources and continuing
    with available data.
    """
    
    def __init__(
        self,
        searcher: Optional[WebSearcher] = None,
        extractor: Optional[ContentExtractor] = None,
        summarizer: Optional[Summarizer] = None,
        reasoning_chain: Optional[ReasoningChain] = None,
        formatter: Optional[OutputFormatter] = None,
        language_detector: Optional[LanguageDetector] = None
    ):
        """
        Initialize the research agent with all components.
        
        Args:
            searcher: Web searcher instance (creates default if None)
            extractor: Content extractor instance (creates default if None)
            summarizer: Summarizer instance (creates default if None)
            reasoning_chain: Reasoning chain instance (creates default if None)
            formatter: Output formatter instance (creates default if None)
            language_detector: Language detector instance (creates default if None)
        """
        self.searcher = searcher or WebSearcher()
        self.extractor = extractor or ContentExtractor()
        self.summarizer = summarizer or Summarizer()
        self.reasoning_chain = reasoning_chain or ReasoningChain()
        self.formatter = formatter or OutputFormatter()
        self.language_detector = language_detector or LanguageDetector()

    async def research(
        self,
        topic: str,
        num_sources: int,
        output_format: str,
        progress_callback: Optional[Callable[[ProgressEvent], Awaitable[None]]] = None
    ) -> str:
        """
        Execute the full research workflow.
        
        Args:
            topic: The research topic (English or Persian)
            num_sources: Number of sources to fetch (3-10)
            output_format: "json" or "markdown"
            progress_callback: Async function to send progress updates
            
        Returns:
            Formatted research result as string
            
        Raises:
            ResearchError: If all sources fail or critical error occurs
        """
        # Step 1: Detect input language
        language = self.language_detector.detect(topic)
        
        # Step 2: Search for sources
        await self._send_progress(progress_callback, ProgressEvent(
            step="searching",
            message="Searching..."
        ))
        
        search_results = await self.searcher.search(topic, num_sources)
        
        if not search_results:
            raise ResearchError("Unable to search. Please try again.")
        
        await self._send_progress(progress_callback, ProgressEvent(
            step="found",
            message=f"Found {len(search_results)} sources",
            count=len(search_results)
        ))
        
        # Step 3 & 4: Extract content and summarize each source
        summaries = await self._process_sources(
            search_results,
            language,
            progress_callback
        )
        
        if not summaries:
            raise ResearchError("Could not retrieve any sources. Please try a different topic.")
        
        # Step 5: Generate final report with reasoning
        await self._send_progress(progress_callback, ProgressEvent(
            step="analyzing",
            message="Analyzing..."
        ))
        
        report = await self.reasoning_chain.generate_report(
            summaries=summaries,
            topic=topic,
            language=language
        )
        
        if not report:
            raise ResearchError("AI service unavailable. Please try again later.")
        
        # Step 6: Format output
        await self._send_progress(progress_callback, ProgressEvent(
            step="finalizing",
            message="Finalizing..."
        ))
        
        result = self.formatter.format(report, output_format)
        
        await self._send_progress(progress_callback, ProgressEvent(
            step="complete",
            message="Complete"
        ))
        
        return result

    async def _process_sources(
        self,
        search_results: list[SearchResult],
        language: str,
        progress_callback: Optional[Callable[[ProgressEvent], Awaitable[None]]] = None
    ) -> list[SourceSummary]:
        """
        Process all search results: extract content and summarize.
        
        Handles failures gracefully by skipping failed sources and
        continuing with remaining ones.
        
        Args:
            search_results: List of search results to process
            language: Detected language for summaries
            progress_callback: Async function to send progress updates
            
        Returns:
            List of successfully processed SourceSummary objects
        """
        summaries: list[SourceSummary] = []
        total = len(search_results)
        source_number = 0
        
        for i, result in enumerate(search_results, 1):
            # Send fetching progress
            await self._send_progress(progress_callback, ProgressEvent(
                step="fetching",
                message=f"Fetching {i}/{total}...",
                current=i,
                total=total
            ))
            
            # Extract content (silently skip on failure per Req 5.4, 5.5)
            extracted = await self.extractor.extract(result.url)
            if not extracted:
                continue
            
            # Apply smart truncation
            truncated_content = self.extractor.smart_truncate(extracted.content)
            
            # Send summarizing progress
            await self._send_progress(progress_callback, ProgressEvent(
                step="summarizing",
                message=f"Summarizing {i}/{total}...",
                current=i,
                total=total
            ))
            
            # Summarize content (silently skip on failure per Req 6.4)
            summary_text = await self.summarizer.summarize(
                content=truncated_content,
                source_title=extracted.title,
                language=language
            )
            
            if not summary_text:
                continue
            
            # Successfully processed - add to summaries
            source_number += 1
            summaries.append(SourceSummary(
                source_number=source_number,
                title=extracted.title,
                url=result.url,
                summary=summary_text
            ))
        
        return summaries

    async def _send_progress(
        self,
        callback: Optional[Callable[[ProgressEvent], Awaitable[None]]],
        event: ProgressEvent
    ) -> None:
        """
        Send progress event via callback if provided.
        
        Args:
            callback: Async callback function to send progress
            event: Progress event to send
        """
        if callback:
            try:
                await callback(event)
            except Exception:
                # Don't let progress callback errors break the workflow
                pass


class ResearchError(Exception):
    """
    Custom exception for research workflow errors.
    
    Contains user-friendly error messages that are safe to display.
    Never contains technical details, stack traces, or sensitive information.
    """
    
    def __init__(self, message: str):
        """
        Initialize with user-friendly message.
        
        Args:
            message: User-friendly error message (safe to display)
        """
        self.message = message
        super().__init__(message)
