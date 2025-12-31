"""
Common interfaces used across features.

Provides base protocols that can be extended by feature-specific interfaces.
"""

from src.shared.interfaces.base import AsyncService, ProgressReporter

__all__ = ["AsyncService", "ProgressReporter"]
