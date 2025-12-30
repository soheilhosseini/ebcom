"""
Data models for the Research AI Assistant.

This module defines all Pydantic models used throughout the application
for request/response handling and internal data structures.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


# Request Models

class ResearchRequest(BaseModel):
    """Request model for initiating a research task."""
    topic: str = Field(..., min_length=1, max_length=500)
    num_sources: int = Field(default=5, ge=3, le=10)
    output_format: Literal["json", "markdown"] = "markdown"

    @field_validator('topic')
    @classmethod
    def topic_not_whitespace_only(cls, v: str) -> str:
        """Reject topics that are empty or contain only whitespace."""
        if not v.strip():
            raise ValueError('Topic cannot be empty or whitespace only')
        return v


# Internal Models

class SearchResult(BaseModel):
    """Result from web search."""
    url: str
    title: str
    snippet: str


class ExtractedContent(BaseModel):
    """Extracted content from a webpage."""
    url: str
    title: str
    content: str


class SourceSummary(BaseModel):
    """Summary of a single source."""
    source_number: int
    title: str
    url: str
    summary: str


class Citation(BaseModel):
    """Citation reference for the final report."""
    number: int
    title: str
    url: str


class FinalReport(BaseModel):
    """Final research report with all sections."""
    summary: str
    key_points: List[str]
    comparison: str
    citations: List[Citation]
    language: str


# Response Models

class ProgressEvent(BaseModel):
    """Progress event for SSE streaming."""
    step: str
    message: str
    current: Optional[int] = None
    total: Optional[int] = None
    count: Optional[int] = None


class ResearchResponse(BaseModel):
    """Final research response."""
    result: str
    format: str


class ErrorResponse(BaseModel):
    """Error response model - never exposes technical details."""
    error: bool = True
    message: str
