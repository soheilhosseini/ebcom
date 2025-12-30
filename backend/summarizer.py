"""
Summarization module for the Research AI Assistant.

This module provides GPT-4o powered summarization functionality
to generate one-paragraph summaries of extracted content.
"""

import os
from typing import Optional

from openai import AsyncOpenAI, OpenAIError


class Summarizer:
    """
    Generates summaries using OpenAI GPT-4o.
    
    Creates one-paragraph summaries of source content in the detected
    input language. Handles API failures gracefully by returning None.
    """
    
    MODEL = "gpt-4o"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the summarizer with OpenAI client.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def summarize(
        self,
        content: str,
        source_title: str,
        language: str
    ) -> Optional[str]:
        """
        Generate a one-paragraph summary of the content.
        
        Args:
            content: Extracted content to summarize
            source_title: Title of the source for context
            language: Output language code ("en" for English, "fa" for Persian)
            
        Returns:
            One-paragraph summary in the specified language,
            or None if summarization fails.
        """
        if not content or not content.strip():
            return None
        
        language_instruction = self._get_language_instruction(language)
        
        system_prompt = f"""You are a research assistant that creates concise, informative summaries.
{language_instruction}
Your task is to summarize the provided content in exactly one paragraph.
Focus on preserving key facts, findings, and important information.
Keep the summary clear and informative."""

        user_prompt = f"""Please summarize the following content from "{source_title}" in one paragraph:

{content}"""

        try:
            response = await self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            summary = response.choices[0].message.content
            return summary.strip() if summary else None
            
        except OpenAIError:
            # Handle API failures gracefully - return None to skip this source
            return None
        except Exception:
            # Handle any unexpected errors gracefully
            return None
    
    def _get_language_instruction(self, language: str) -> str:
        """
        Get language-specific instruction for the prompt.
        
        Args:
            language: Language code ("en" or "fa")
            
        Returns:
            Instruction string for the specified language
        """
        if language == "fa":
            return "You MUST write your response entirely in Persian (Farsi). Do not use English."
        return "You MUST write your response entirely in English. Do not use other languages."
