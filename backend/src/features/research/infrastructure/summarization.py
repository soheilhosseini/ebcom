"""
OpenAI-based summarization implementation.
"""

from typing import Optional

from openai import AsyncOpenAI, OpenAIError

from src.shared.config import settings
from src.features.research.infrastructure.prompts import (
    get_language_instruction,
    SUMMARIZATION_SYSTEM,
    SUMMARIZATION_USER,
)


class OpenAISummarizer:
    """Summarization using OpenAI GPT-5 Nano."""
    
    def __init__(self, api_key: str = None):
        self._api_key = api_key or settings.openai_api_key
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
                model=settings.llm.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.llm.temperature,
                max_tokens=settings.llm.summary_max_tokens
            )
            
            summary = response.choices[0].message.content
            return summary.strip() if summary else None
            
        except (OpenAIError, Exception):
            return None
