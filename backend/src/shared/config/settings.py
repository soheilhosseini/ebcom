"""
Application settings and configuration.

Centralizes all configuration values with environment variable support.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass(frozen=True)
class LLMSettings:
    """Settings for LLM (Language Model) services."""
    model: str = "gpt-5-nano"
    temperature: float = 0.3
    summary_max_tokens: int = 500
    api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))


@dataclass(frozen=True)
class ResearchSettings:
    """Settings for research feature."""
    min_sources: int = 3
    max_sources: int = 10
    default_sources: int = 5
    max_topic_length: int = 500
    fetch_timeout_seconds: int = 15
    max_content_chars: int = 8000  # ~2000 tokens


@dataclass(frozen=True)
class ServerSettings:
    """Settings for server configuration."""
    host: str = "0.0.0.0"
    port: int = 8501
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")


@dataclass
class Settings:
    """
    Application settings container.
    
    Provides typed access to all configuration values.
    """
    llm: LLMSettings = field(default_factory=LLMSettings)
    research: ResearchSettings = field(default_factory=ResearchSettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Convenience accessor for OpenAI API key."""
        return self.llm.api_key


# Global settings instance
settings = Settings()
