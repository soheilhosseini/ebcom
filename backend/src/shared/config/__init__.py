"""
Configuration management module.

Provides centralized configuration using environment variables
and sensible defaults.
"""

from src.shared.config.settings import Settings, settings

__all__ = ["Settings", "settings"]
