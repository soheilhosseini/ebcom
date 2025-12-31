"""
Research service - main business logic orchestrator.
"""

from typing import Callable, Optional, Awaitable, List

from src.features.research.domain.models import (
    ProgressEvent,
    SearchResult,
    SourceSummary,
    ResearchResult,
)
from src.features.research.domain.interfaces import (
    SearchProvider,
    ContentExtractor,
    Summarizer,
    ReportGenerator,
    LanguageDetector,
    OutputFormatter,
)
from src.features.research.domain.enums import ProgressStep
from src.features.research.domain.exceptions import (
    SearchFailedError,
    NoSourcesFoundError,
    AIServiceError,
)


ProgressCallback = Optional[Callable[[ProgressEvent], Awaitable[None]]]


class ResearchService:
    """Orchestrates the research workflow."""
    
    def __init__(
        self,
        search: SearchProvider,
        extractor: ContentExtractor,
        summarizer: Summarizer,
        report_generator: ReportGenerator,
        language_detector: LanguageDetector,
        formatter: OutputFormatter,
    ):
        self._search = search
        self._extractor = extractor
        self._summarizer = summarizer
        self._report_gen = report_generator
        self._lang_detect = language_detector
        self._formatter = formatter

    async def research(
        self,
        topic: str,
        num_sources: int,
        progress_callback: ProgressCallback = None
    ) -> ResearchResult:
        """Execute the complete research workflow."""
        language = self._lang_detect.detect(topic)
        
        # Search
        results = await self._search_sources(topic, num_sources, progress_callback)
        
        # Process sources
        summaries = await self._process_sources(results, language, progress_callback)
        if not summaries:
            raise NoSourcesFoundError()
        
        # Generate report
        report = await self._generate_report(summaries, topic, language, progress_callback)
        if not report:
            raise AIServiceError()
        
        await self._emit(progress_callback, ProgressStep.COMPLETE, "Complete")
        
        return ResearchResult(report=report, language=language)
    
    async def _search_sources(
        self,
        topic: str,
        num_sources: int,
        callback: ProgressCallback
    ) -> List[SearchResult]:
        """Search for sources."""
        await self._emit(callback, ProgressStep.SEARCHING, "Searching...")
        
        results = await self._search.search(topic, num_sources)
        if not results:
            raise SearchFailedError()
        
        await self._emit(
            callback, ProgressStep.FOUND,
            f"Found {len(results)} sources",
            count=len(results)
        )
        return results

    async def _process_sources(
        self,
        results: List[SearchResult],
        language: str,
        callback: ProgressCallback
    ) -> List[SourceSummary]:
        """Extract and summarize all sources."""
        summaries = []
        total = len(results)
        source_num = 0
        
        for i, result in enumerate(results, 1):
            # Extract
            await self._emit(
                callback, ProgressStep.FETCHING,
                f"Fetching {i}/{total}...",
                current=i, total=total
            )
            
            extracted = await self._extractor.extract(result.url)
            if not extracted:
                continue
            
            truncated = self._extractor.truncate(extracted.content)
            
            # Summarize
            await self._emit(
                callback, ProgressStep.SUMMARIZING,
                f"Summarizing {i}/{total}...",
                current=i, total=total
            )
            
            summary = await self._summarizer.summarize(
                truncated, extracted.title, language
            )
            if not summary:
                continue
            
            source_num += 1
            summaries.append(SourceSummary(
                source_number=source_num,
                title=extracted.title,
                url=result.url,
                summary=summary
            ))
        
        return summaries
    
    async def _generate_report(self, summaries, topic, language, callback):
        """Generate the final report."""
        await self._emit(callback, ProgressStep.ANALYZING, "Analyzing...")
        return await self._report_gen.generate(summaries, topic, language)
    
    async def _emit(
        self,
        callback: ProgressCallback,
        step: ProgressStep,
        message: str,
        current: int = None,
        total: int = None,
        count: int = None
    ):
        """Emit progress event."""
        if not callback:
            return
        try:
            await callback(ProgressEvent(
                step=step.value,
                message=message,
                current=current,
                total=total,
                count=count
            ))
        except Exception:
            pass
