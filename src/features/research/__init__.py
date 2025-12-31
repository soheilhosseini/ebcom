"""
Research feature module.

Provides AI-powered research capabilities including:
- Web search and content extraction
- Content summarization
- Report generation with citations
- Multi-language support (English/Persian)
"""

from src.features.research.services import ResearchService
from src.features.research.domain import ResearchRequest, ResearchResult

__all__ = ["ResearchService", "ResearchRequest", "ResearchResult"]
