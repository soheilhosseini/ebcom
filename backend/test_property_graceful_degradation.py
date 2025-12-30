"""
Property-based test for graceful source degradation.

**Feature: research-ai-assistant, Property 7: Graceful Source Degradation**
**Validates: Requirements 4.3**

Property 7: Graceful Source Degradation
*For any* search that returns M sources where M < N (requested), the Research_Agent
SHALL proceed with M sources and produce a valid report.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, MagicMock

from research_agent import ResearchAgent
from models import (
    SearchResult,
    ExtractedContent,
    SourceSummary,
    FinalReport,
    Citation
)


# Strategy for requested source count (3-10)
requested_sources = st.integers(min_value=3, max_value=10)


@st.composite
def degraded_source_scenario(draw):
    """Generate a scenario where available sources < requested sources."""
    requested = draw(st.integers(min_value=3, max_value=10))
    # Available must be at least 1 (otherwise it's a complete failure, not degradation)
    # and less than requested
    available = draw(st.integers(min_value=1, max_value=max(1, requested - 1)))
    return requested, available


def create_mock_agent():
    """Create a ResearchAgent with all components mocked to avoid API calls."""
    mock_searcher = MagicMock()
    mock_extractor = MagicMock()
    mock_summarizer = MagicMock()
    mock_reasoning_chain = MagicMock()
    mock_formatter = MagicMock()
    mock_language_detector = MagicMock()
    
    agent = ResearchAgent(
        searcher=mock_searcher,
        extractor=mock_extractor,
        summarizer=mock_summarizer,
        reasoning_chain=mock_reasoning_chain,
        formatter=mock_formatter,
        language_detector=mock_language_detector
    )
    
    return agent


@given(scenario=degraded_source_scenario())
@settings(max_examples=100)
def test_property_graceful_degradation_proceeds_with_available_sources(scenario):
    """
    **Feature: research-ai-assistant, Property 7: Graceful Source Degradation**
    **Validates: Requirements 4.3**
    
    For any search that returns M sources where M < N (requested), the Research_Agent
    SHALL proceed with M sources and produce a valid report.
    """
    requested, available = scenario
    
    # Create mock search results (fewer than requested)
    mock_search_results = [
        SearchResult(
            url=f"https://example{i}.com",
            title=f"Title {i}",
            snippet=f"Snippet {i}"
        )
        for i in range(available)
    ]
    
    # Create mock extracted content for each source
    mock_extracted_contents = [
        ExtractedContent(
            url=f"https://example{i}.com",
            title=f"Title {i}",
            content=f"Content for source {i}. This is the main article text."
        )
        for i in range(available)
    ]
    
    # Create mock final report
    mock_report = FinalReport(
        summary="Combined summary of all sources",
        key_points=["Key point 1", "Key point 2"],
        comparison="Comparison of sources",
        citations=[
            Citation(number=i+1, title=f"Title {i}", url=f"https://example{i}.com")
            for i in range(available)
        ],
        language="en"
    )
    
    # Create the agent with mocked components
    agent = create_mock_agent()
    
    # Mock the searcher to return fewer results than requested
    agent.searcher.search = AsyncMock(return_value=mock_search_results)
    
    # Mock the extractor to return content for each source
    extract_call_count = [0]
    async def mock_extract(url):
        idx = extract_call_count[0]
        extract_call_count[0] += 1
        if idx < len(mock_extracted_contents):
            return mock_extracted_contents[idx]
        return None
    
    agent.extractor.extract = mock_extract
    agent.extractor.smart_truncate = MagicMock(side_effect=lambda x: x[:500])
    
    # Mock the summarizer
    summarize_call_count = [0]
    async def mock_summarize(content, source_title, language):
        idx = summarize_call_count[0]
        summarize_call_count[0] += 1
        return f"Summary {idx}"
    
    agent.summarizer.summarize = mock_summarize
    
    # Mock the reasoning chain
    agent.reasoning_chain.generate_report = AsyncMock(return_value=mock_report)
    
    # Mock the formatter
    agent.formatter.format = MagicMock(return_value="Formatted output")
    
    # Mock language detector
    agent.language_detector.detect = MagicMock(return_value="en")
    
    # Execute the research
    import asyncio
    result = asyncio.run(agent.research(
        topic="test topic",
        num_sources=requested,
        output_format="markdown"
    ))
    
    # Verify the agent proceeded with available sources
    # 1. Search was called with requested count
    agent.searcher.search.assert_called_once_with("test topic", requested)
    
    # 2. The agent produced a result (didn't fail)
    assert result is not None, "Agent should produce a result with degraded sources"
    assert result == "Formatted output", "Agent should return formatted output"
    
    # 3. The reasoning chain was called (report was generated)
    agent.reasoning_chain.generate_report.assert_called_once()
    
    # 4. The formatter was called (output was formatted)
    agent.formatter.format.assert_called_once()


@given(scenario=degraded_source_scenario())
@settings(max_examples=100)
def test_property_graceful_degradation_report_reflects_available_sources(scenario):
    """
    **Feature: research-ai-assistant, Property 7: Graceful Source Degradation**
    **Validates: Requirements 4.3**
    
    For any degraded scenario, the final report SHALL contain citations
    only for the sources that were successfully processed.
    """
    requested, available = scenario
    
    # Create mock search results
    mock_search_results = [
        SearchResult(
            url=f"https://example{i}.com",
            title=f"Title {i}",
            snippet=f"Snippet {i}"
        )
        for i in range(available)
    ]
    
    # Create mock extracted content
    mock_extracted_contents = [
        ExtractedContent(
            url=f"https://example{i}.com",
            title=f"Title {i}",
            content=f"Content for source {i}"
        )
        for i in range(available)
    ]
    
    # Track summaries passed to reasoning chain
    captured_summaries = []
    
    # Create mock final report based on available sources
    mock_report = FinalReport(
        summary="Summary",
        key_points=["Point 1"],
        comparison="Comparison",
        citations=[
            Citation(number=i+1, title=f"Title {i}", url=f"https://example{i}.com")
            for i in range(available)
        ],
        language="en"
    )
    
    agent = create_mock_agent()
    
    # Mock components
    agent.searcher.search = AsyncMock(return_value=mock_search_results)
    
    extract_idx = [0]
    async def mock_extract(url):
        idx = extract_idx[0]
        extract_idx[0] += 1
        if idx < len(mock_extracted_contents):
            return mock_extracted_contents[idx]
        return None
    
    agent.extractor.extract = mock_extract
    agent.extractor.smart_truncate = MagicMock(side_effect=lambda x: x)
    
    async def mock_summarize(content, source_title, language):
        return "Summary"
    
    agent.summarizer.summarize = mock_summarize
    
    async def mock_generate_report(summaries, topic, language):
        captured_summaries.extend(summaries)
        return mock_report
    
    agent.reasoning_chain.generate_report = mock_generate_report
    agent.formatter.format = MagicMock(return_value="Output")
    agent.language_detector.detect = MagicMock(return_value="en")
    
    import asyncio
    asyncio.run(agent.research(
        topic="test",
        num_sources=requested,
        output_format="markdown"
    ))
    
    # Verify the number of summaries passed to reasoning chain matches available
    assert len(captured_summaries) == available, (
        f"Expected {available} summaries, got {len(captured_summaries)}"
    )


@given(requested=requested_sources)
@settings(max_examples=100)
def test_property_graceful_degradation_with_partial_extraction_failures(requested: int):
    """
    **Feature: research-ai-assistant, Property 7: Graceful Source Degradation**
    **Validates: Requirements 4.3**
    
    For any scenario where some extractions fail, the Research_Agent SHALL
    proceed with successfully extracted sources.
    """
    # Simulate: search returns requested count, but half fail extraction
    successful_extractions = max(1, requested // 2)
    
    mock_search_results = [
        SearchResult(
            url=f"https://example{i}.com",
            title=f"Title {i}",
            snippet=f"Snippet {i}"
        )
        for i in range(requested)
    ]
    
    mock_report = FinalReport(
        summary="Summary",
        key_points=["Point"],
        comparison="Comparison",
        citations=[
            Citation(number=i+1, title=f"Title {i}", url=f"https://example{i}.com")
            for i in range(successful_extractions)
        ],
        language="en"
    )
    
    agent = create_mock_agent()
    agent.searcher.search = AsyncMock(return_value=mock_search_results)
    
    # Only first half of extractions succeed
    extract_idx = [0]
    async def mock_extract(url):
        idx = extract_idx[0]
        extract_idx[0] += 1
        if idx < successful_extractions:
            return ExtractedContent(
                url=url,
                title=f"Title {idx}",
                content=f"Content {idx}"
            )
        return None  # Extraction failure
    
    agent.extractor.extract = mock_extract
    agent.extractor.smart_truncate = MagicMock(side_effect=lambda x: x)
    
    async def mock_summarize(content, source_title, language):
        return "Summary"
    
    agent.summarizer.summarize = mock_summarize
    agent.reasoning_chain.generate_report = AsyncMock(return_value=mock_report)
    agent.formatter.format = MagicMock(return_value="Output")
    agent.language_detector.detect = MagicMock(return_value="en")
    
    import asyncio
    result = asyncio.run(agent.research(
        topic="test",
        num_sources=requested,
        output_format="markdown"
    ))
    
    # Agent should produce a result despite partial failures
    assert result is not None
    assert result == "Output"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
