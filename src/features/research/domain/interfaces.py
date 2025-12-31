"""
Interfaces (protocols) for the research feature.

Defines contracts that infrastructure implementations must fulfill.
"""

from typing import Protocol, List, Optional, runtime_checkable

from src.features.research.domain.models import (
    SearchResult,
    ExtractedContent,
    SourceSummary,
    FinalReport,
)


@runtime_checkable
class SearchProvider(Protocol):
    """Interface for web search functionality."""
    
    async def search(self, query: str, num_results: int) -> List[SearchResult]:
        """Search the web for relevant sources."""
        ...


@runtime_checkable
class ContentExtractor(Protocol):
    """Interface for webpage content extraction."""
    
    async def extract(self, url: str) -> Optional[ExtractedContent]:
        """Extract main content from a webpage."""
        ...
    
    def truncate(self, content: str, max_chars: int) -> str:
        """Truncate content while preserving structure."""
        ...


@runtime_checkable
class Summarizer(Protocol):
    """Interface for content summarization."""
    
    async def summarize(
        self,
        content: str,
        source_title: str,
        language: str
    ) -> Optional[str]:
        """Generate a summary of the content."""
        ...


@runtime_checkable
class ReportGenerator(Protocol):
    """Interface for final report generation."""
    
    async def generate(
        self,
        summaries: List[SourceSummary],
        topic: str,
        language: str
    ) -> Optional[FinalReport]:
        """Generate a final research report."""
        ...


@runtime_checkable
class LanguageDetector(Protocol):
    """Interface for language detection."""
    
    def detect(self, text: str) -> str:
        """Detect the language of input text."""
        ...


@runtime_checkable
class OutputFormatter(Protocol):
    """Interface for output formatting."""
    
    def format(self, report: FinalReport, format_type: str) -> str:
        """Format a report into the specified format."""
        ...
