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

from src.features.research.domain.models import ResearchRequest, ProgressEvent
from src.features.research.domain.enums import OutputFormat
from src.features.research.domain.exceptions import ResearchError
from src.features.research.services import create_research_service

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
    """
    return StreamingResponse(
        research_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


async def research_stream(request: ResearchRequest) -> AsyncGenerator[str, None]:
    """Generate SSE events for the research workflow."""
    progress_queue: asyncio.Queue[ProgressEvent] = asyncio.Queue()
    
    async def progress_callback(event: ProgressEvent) -> None:
        await progress_queue.put(event)
    
    service = create_research_service()
    
    research_task = asyncio.create_task(
        service.research(
            topic=request.topic,
            num_sources=request.num_sources,
            output_format=request.output_format,
            progress_callback=progress_callback
        )
    )
    
    try:
        while not research_task.done():
            try:
                event = await asyncio.wait_for(progress_queue.get(), timeout=0.5)
                yield format_sse_event("progress", event.model_dump())
            except asyncio.TimeoutError:
                continue
        
        while not progress_queue.empty():
            event = await progress_queue.get()
            yield format_sse_event("progress", event.model_dump())
        
        result = await research_task
        yield format_sse_event("complete", {
            "result": result.content,
            "format": request.output_format.value
        })
        
    except ResearchError as e:
        yield format_sse_event("error", {"message": e.message})
    except Exception:
        yield format_sse_event("error", {
            "message": "An unexpected error occurred. Please try again."
        })


def format_sse_event(event_type: str, data: dict) -> str:
    """Format data as an SSE event string."""
    json_data = json.dumps(data)
    return f"event: {event_type}\ndata: {json_data}\n\n"
