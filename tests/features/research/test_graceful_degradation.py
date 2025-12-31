"""
Property-based test for graceful source degradation.

**Feature: research-ai-assistant, Property 7: Graceful Source Degradation**
**Validates: Requirements 4.3**
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, MagicMock
import asyncio

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.features.research.services.research_service import ResearchService
from src.features.research.domain.models import (
    SearchResult, ExtractedContent, SourceSummary, FinalReport, Citation
)


requested_sources = st.integers(min_value=3, max_value=10)


@st.composite
def degraded_source_scenario(draw):
    requested = draw(st.integers(min_value=3, max_value=10))
    available = draw(st.integers(min_value=1, max_value=max(1, requested - 1)))
    return requested, available


def create_mock_service():
    """Create ResearchService with mocked dependencies."""
    mock_search = MagicMock()
    mock_extractor = MagicMock()
    mock_summarizer = MagicMock()
    mock_report_gen = MagicMock()
    mock_lang_detect = MagicMock()
    mock_formatter = MagicMock()
    
    service = ResearchService(
        search=mock_search,
        extractor=mock_extractor,
        summarizer=mock_summarizer,
        report_generator=mock_report_gen,
        language_detector=mock_lang_detect,
        formatter=mock_formatter,
    )
    return service


@given(scenario=degraded_source_scenario())
@settings(max_examples=100)
def test_property_graceful_degradation_proceeds_with_available_sources(scenario):
    """Property 7: Agent proceeds with M sources when M < N requested."""
    requested, available = scenario
    
    mock_search_results = [
        SearchResult(url=f"https://example{i}.com", title=f"Title {i}", snippet=f"Snippet {i}")
        for i in range(available)
    ]
    
    mock_report = FinalReport(
        summary="Summary", key_points=["Point 1"], comparison="Comparison",
        citations=[Citation(number=i+1, title=f"Title {i}", url=f"https://example{i}.com") for i in range(available)],
        language="en"
    )
    
    service = create_mock_service()
    service._search.search = AsyncMock(return_value=mock_search_results)
    service._lang_detect.detect = MagicMock(return_value="en")
    
    extract_idx = [0]
    async def mock_extract(url):
        idx = extract_idx[0]
        extract_idx[0] += 1
        return ExtractedContent(url=url, title=f"Title {idx}", content=f"Content {idx}")
    
    service._extractor.extract = mock_extract
    service._extractor.truncate = MagicMock(side_effect=lambda x: x[:500])
    
    async def mock_summarize(content, title, lang):
        return "Summary"
    
    service._summarizer.summarize = mock_summarize
    service._report_gen.generate = AsyncMock(return_value=mock_report)
    service._formatter.format = MagicMock(return_value="Formatted output")
    
    result = asyncio.run(service.research(
        topic="test topic", num_sources=requested
    ))
    
    assert result is not None
    assert result.report is not None
