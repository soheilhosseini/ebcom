"""
OpenAI-based summarization implementation.
"""

from typing import Optional

from openai import AsyncOpenAI, OpenAIError, APIError, AuthenticationError, RateLimitError

from src.shared.config import settings
from src.features.research.infrastructure.prompts import (
    get_language_instruction,
    SUMMARIZATION_SYSTEM,
    SUMMARIZATION_USER,
)
from src.features.research.domain.exceptions import AIServiceError


class OpenAISummarizer:
    """Summarization using OpenAI."""
    
    def __init__(self, api_key: str = None, model: str = None):
        self._api_key = api_key or settings.openai_api_key
        self._model = model or settings.llm.model
        self._client = AsyncOpenAI(api_key=self._api_key)
    
    async def summarize(
        self,
        content: str,
        source_title: str,
        language: str
    ) -> Optional[str]:
        """Generate a one-paragraph summary."""
        if not content or not content.strip():
            return None
        
        system_prompt = SUMMARIZATION_SYSTEM.format(
            language_instruction=get_language_instruction(language)
        )
        user_prompt = SUMMARIZATION_USER.format(
            source_title=source_title,
            content=content
        )
        
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.llm.temperature,
                max_tokens=settings.llm.summary_max_tokens
            )
            
            summary = response.choices[0].message.content
            return summary.strip() if summary else None
            
        except AuthenticationError:
            raise AIServiceError("Invalid OpenAI API key. Please check your API key in .env file.")
        except RateLimitError:
            raise AIServiceError("OpenAI rate limit exceeded. Please wait and try again.")
        except APIError as e:
            raise AIServiceError(f"OpenAI API error: {e.message}")
        except Exception as e:
            raise AIServiceError(f"AI service error: {str(e)}")
