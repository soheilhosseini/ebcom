"""
Base exceptions for the application.

Provides a hierarchy of exceptions that features can extend.
"""

from src.shared.exceptions.base import AppError, ValidationError, ServiceError

__all__ = ["AppError", "ValidationError", "ServiceError"]
