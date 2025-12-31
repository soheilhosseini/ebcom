"""
Domain models for the research feature.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from src.shared.config import settings
from src.features.research.domain.enums import OutputFormat


class ResearchRequest(BaseModel):
    """Request to initiate a research task."""
    topic: str = Field(
        ...,
        min_length=1,
        max_length=settings.research.max_topic_length,
        description="The research topic to investigate"
    )
    num_sources: int = Field(
        default=settings.research.default_sources,
        ge=settings.research.min_sources,
        le=settings.research.max_sources,
        description="Number of sources to fetch and analyze"
    )
    output_format: OutputFormat = Field(
        default=OutputFormat.MARKDOWN,
        description="Format for the research output"
    )

    @field_validator("topic")
    @classmethod
    def validate_topic_not_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Topic cannot be empty or whitespace only")
        return value


class SearchResult(BaseModel):
    """Result from a web search query."""
    url: str
    title: str
    snippet: str


class ExtractedContent(BaseModel):
    """Content extracted from a webpage."""
    url: str
    title: str
    content: str


class SourceSummary(BaseModel):
    """Summary of a single source with metadata."""
    source_number: int = Field(..., ge=1)
    title: str
    url: str
    summary: str


class Citation(BaseModel):
    """Citation reference for the final report."""
    number: int = Field(..., ge=1)
    title: str
    url: str


class FinalReport(BaseModel):
    """Complete research report with all sections."""
    summary: str
    key_points: List[str]
    comparison: str
    citations: List[Citation]
    language: str


class ProgressEvent(BaseModel):
    """Progress event for real-time updates."""
    step: str
    message: str
    current: Optional[int] = None
    total: Optional[int] = None
    count: Optional[int] = None


class ResearchResult(BaseModel):
    """Final research result."""
    content: str
    format: OutputFormat
    language: str
