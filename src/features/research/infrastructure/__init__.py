"""
Infrastructure layer for the research feature.

Contains implementations of domain interfaces using external services.
"""

from src.features.research.infrastructure.search import DuckDuckGoSearch
from src.features.research.infrastructure.extraction import TrafilaturaExtractor
from src.features.research.infrastructure.summarization import OpenAISummarizer
from src.features.research.infrastructure.report import LangChainReportGenerator
from src.features.research.infrastructure.language import LangDetectLanguageDetector
from src.features.research.infrastructure.formatting import MarkdownJsonFormatter

__all__ = [
    "DuckDuckGoSearch",
    "TrafilaturaExtractor",
    "OpenAISummarizer",
    "LangChainReportGenerator",
    "LangDetectLanguageDetector",
    "MarkdownJsonFormatter",
]
