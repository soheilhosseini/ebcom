"""
Shared module containing cross-cutting concerns.

This module provides utilities, configurations, and base classes
that are shared across all features.
"""

from src.shared.config import settings
from src.shared.exceptions import AppError

__all__ = ["settings", "AppError"]
