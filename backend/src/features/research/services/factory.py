"""
Factory for creating research service with dependencies.
"""

from src.features.research.services.research_service import ResearchService
from src.features.research.infrastructure import (
    DuckDuckGoSearch,
    TrafilaturaExtractor,
    OpenAISummarizer,
    LangChainReportGenerator,
    LangDetectLanguageDetector,
    MarkdownJsonFormatter,
)


def create_research_service(api_key: str = None) -> ResearchService:
    """
    Create a fully configured ResearchService.
    
    Args:
        api_key: Optional OpenAI API key (uses env var if not provided)
        
    Returns:
        Configured ResearchService instance
    """
    return ResearchService(
        search=DuckDuckGoSearch(),
        extractor=TrafilaturaExtractor(),
        summarizer=OpenAISummarizer(api_key=api_key),
        report_generator=LangChainReportGenerator(api_key=api_key),
        language_detector=LangDetectLanguageDetector(),
        formatter=MarkdownJsonFormatter(),
    )
