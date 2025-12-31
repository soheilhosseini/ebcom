"""
Base interfaces for the application.

Defines common protocols that services can implement.
"""

from typing import Protocol, Any, Callable, Awaitable, Optional
from dataclasses import dataclass


@dataclass
class ProgressUpdate:
    """Generic progress update for long-running operations."""
    step: str
    message: str
    progress: float = 0.0  # 0.0 to 1.0
    metadata: Optional[dict] = None


# Type alias for progress callbacks
ProgressCallback = Optional[Callable[[ProgressUpdate], Awaitable[None]]]


class AsyncService(Protocol):
    """Base protocol for async services."""
    
    async def health_check(self) -> bool:
        """Check if the service is healthy."""
        ...


class ProgressReporter(Protocol):
    """Protocol for services that report progress."""
    
    async def report_progress(self, update: ProgressUpdate) -> None:
        """Report progress to listeners."""
        ...
