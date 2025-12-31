"""
Research feature domain layer.

Contains domain models, value objects, and interfaces specific
to the research feature.
"""

from src.features.research.domain.models import (
    ResearchRequest,
    ResearchResult,
    SearchResult,
    ExtractedContent,
    SourceSummary,
    Citation,
    FinalReport,
    ProgressEvent,
)
from src.features.research.domain.enums import OutputFormat, SupportedLanguage
from src.features.research.domain.interfaces import (
    SearchProvider,
    ContentExtractor,
    Summarizer,
    ReportGenerator,
    LanguageDetector,
    OutputFormatter,
)
from src.features.research.domain.exceptions import (
    ResearchError,
    SearchFailedError,
    NoSourcesFoundError,
    AIServiceError,
)

__all__ = [
    # Models
    "ResearchRequest",
    "ResearchResult",
    "SearchResult",
    "ExtractedContent",
    "SourceSummary",
    "Citation",
    "FinalReport",
    "ProgressEvent",
    # Enums
    "OutputFormat",
    "SupportedLanguage",
    # Interfaces
    "SearchProvider",
    "ContentExtractor",
    "Summarizer",
    "ReportGenerator",
    "LanguageDetector",
    "OutputFormatter",
    # Exceptions
    "ResearchError",
    "SearchFailedError",
    "NoSourcesFoundError",
    "AIServiceError",
]
