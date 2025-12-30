"""
Research AI Assistant - FastAPI Backend

A multi-step intelligent agent that helps users research any topic by searching
the web, extracting content from sources, generating summaries, and producing
a comprehensive final report with citations.
"""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from models import ResearchRequest, ProgressEvent, ErrorResponse
from research_agent import ResearchAgent, ResearchError

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Research AI Assistant",
    description="A multi-step intelligent agent for comprehensive topic research",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Research AI Assistant API"}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


@app.post("/api/research")
async def research(request: ResearchRequest):
    """
    Execute a research request and stream progress via SSE.
    
    This endpoint initiates a research workflow and returns a Server-Sent Events
    stream with real-time progress updates. The stream includes:
    - progress events: Step-by-step updates during research
    - complete event: Final result when research completes
    - error event: Error message if research fails
    
    Args:
        request: ResearchRequest with topic, num_sources, and output_format
        
    Returns:
        StreamingResponse with SSE events
    """
    return StreamingResponse(
        research_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


async def research_stream(request: ResearchRequest) -> AsyncGenerator[str, None]:
    """
    Generate SSE events for the research workflow.
    
    Creates an async generator that yields SSE-formatted events as the
    research progresses through each step.
    
    Args:
        request: ResearchRequest with topic, num_sources, and output_format
        
    Yields:
        SSE-formatted strings for progress, complete, or error events
    """
    # Queue to hold progress events
    progress_queue: asyncio.Queue[ProgressEvent] = asyncio.Queue()
    
    async def progress_callback(event: ProgressEvent) -> None:
        """Callback to queue progress events."""
        await progress_queue.put(event)
    
    # Create research agent
    agent = ResearchAgent()
    
    # Start research task
    research_task = asyncio.create_task(
        agent.research(
            topic=request.topic,
            num_sources=request.num_sources,
            output_format=request.output_format,
            progress_callback=progress_callback
        )
    )
    
    try:
        # Stream progress events until research completes
        while not research_task.done():
            try:
                # Wait for progress event with timeout
                event = await asyncio.wait_for(
                    progress_queue.get(),
                    timeout=0.5
                )
                yield format_sse_event("progress", event.model_dump())
            except asyncio.TimeoutError:
                # No event yet, continue waiting
                continue
        
        # Drain any remaining progress events
        while not progress_queue.empty():
            event = await progress_queue.get()
            yield format_sse_event("progress", event.model_dump())
        
        # Get the result (may raise exception)
        result = await research_task
        
        # Send complete event with result
        yield format_sse_event("complete", {
            "result": result,
            "format": request.output_format
        })
        
    except ResearchError as e:
        # Send user-friendly error event
        yield format_sse_event("error", {"message": e.message})
        
    except Exception:
        # Send generic error for unexpected failures
        # Never expose technical details per Requirement 11.5
        yield format_sse_event("error", {
            "message": "An unexpected error occurred. Please try again."
        })



def format_sse_event(event_type: str, data: dict) -> str:
    """
    Format data as an SSE event string.
    
    Creates a properly formatted Server-Sent Events message with
    event type and JSON-encoded data.
    
    Args:
        event_type: The event type (progress, complete, error)
        data: Dictionary to encode as JSON in the data field
        
    Returns:
        SSE-formatted string with event and data fields
    """
    json_data = json.dumps(data)
    return f"event: {event_type}\ndata: {json_data}\n\n"
