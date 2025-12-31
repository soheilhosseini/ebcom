"""
Exceptions specific to the research feature.
"""

from src.shared.exceptions import AppError


class ResearchError(AppError):
    """Base exception for research-related errors."""
    
    def __init__(self, message: str):
        super().__init__(message, code="RESEARCH_ERROR")


class SearchFailedError(ResearchError):
    """Raised when web search fails completely."""
    
    def __init__(self):
        super().__init__("Unable to search. Please try again.")


class NoSourcesFoundError(ResearchError):
    """Raised when no sources could be retrieved or processed."""
    
    def __init__(self):
        super().__init__(
            "Could not retrieve any sources. Please try a different topic."
        )


class AIServiceError(ResearchError):
    """Raised when the AI service is unavailable."""
    
    def __init__(self):
        super().__init__("AI service unavailable. Please try again later.")
