"""
Enumerations for the research feature.
"""

from enum import Enum


class SupportedLanguage(str, Enum):
    """Supported languages for research output."""
    ENGLISH = "en"
    PERSIAN = "fa"
    
    @classmethod
    def get_default(cls) -> "SupportedLanguage":
        return cls.ENGLISH


class OutputFormat(str, Enum):
    """Supported output formats for research results."""
    MARKDOWN = "markdown"
    JSON = "json"
    
    @classmethod
    def get_default(cls) -> "OutputFormat":
        return cls.MARKDOWN


class ProgressStep(str, Enum):
    """Progress steps during research workflow."""
    SEARCHING = "searching"
    FOUND = "found"
    FETCHING = "fetching"
    SUMMARIZING = "summarizing"
    ANALYZING = "analyzing"
    FINALIZING = "finalizing"
    COMPLETE = "complete"
