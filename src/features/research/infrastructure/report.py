"""
LangChain-based report generation implementation.
"""

from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from openai import AuthenticationError, RateLimitError, APIError

from src.shared.config import settings
from src.features.research.domain.models import SourceSummary, FinalReport, Citation
from src.features.research.domain.exceptions import AIServiceError
from src.features.research.infrastructure.prompts import (
    get_language_instruction,
    MAIN_SUMMARY_SYSTEM,
    MAIN_SUMMARY_USER,
    KEY_POINTS_SYSTEM,
    KEY_POINTS_USER,
    COMPARISON_SYSTEM,
    COMPARISON_USER,
)


class LangChainReportGenerator:
    """Report generation using LangChain."""
    
    def __init__(self, api_key: str = None, model: str = None):
        self._llm = ChatOpenAI(
            model=model or settings.llm.model,
            api_key=api_key or settings.openai_api_key,
            temperature=settings.llm.temperature
        )
        self._parser = StrOutputParser()

    async def generate(
        self,
        summaries: List[SourceSummary],
        topic: str,
        language: str
    ) -> Optional[FinalReport]:
        """Generate a final research report."""
        if not summaries:
            return None
        
        try:
            formatted = self._format_summaries(summaries)
            lang_inst = get_language_instruction(language)
            
            main_summary = await self._generate_summary(formatted, topic, lang_inst)
            key_points = await self._extract_key_points(formatted, topic, lang_inst)
            comparison = await self._generate_comparison(formatted, topic, lang_inst)
            
            if not all([main_summary, key_points, comparison]):
                return None
            
            return FinalReport(
                summary=main_summary,
                key_points=key_points,
                comparison=comparison,
                citations=self._build_citations(summaries),
                language=language
            )
        except AIServiceError:
            raise
        except AuthenticationError:
            raise AIServiceError("Invalid OpenAI API key. Please check your API key in .env file.")
        except RateLimitError:
            raise AIServiceError("OpenAI rate limit exceeded. Please wait and try again.")
        except APIError as e:
            raise AIServiceError(f"OpenAI API error: {e.message}")
        except Exception as e:
            raise AIServiceError(f"AI service error: {str(e)}")
    
    def _format_summaries(self, summaries: List[SourceSummary]) -> str:
        """Format summaries for prompts."""
        return "\n".join(
            f"[{s.source_number}] {s.title}\nURL: {s.url}\nSummary: {s.summary}\n"
            for s in summaries
        )
    
    def _build_citations(self, summaries: List[SourceSummary]) -> List[Citation]:
        """Build citation list from summaries."""
        return [
            Citation(number=s.source_number, title=s.title, url=s.url)
            for s in summaries
        ]

    async def _generate_summary(self, summaries: str, topic: str, lang: str) -> Optional[str]:
        """Generate main summary section."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", MAIN_SUMMARY_SYSTEM.format(language_instruction=lang)),
            ("user", MAIN_SUMMARY_USER)
        ])
        chain = prompt | self._llm | self._parser
        try:
            result = await chain.ainvoke({"topic": topic, "summaries": summaries})
            return result.strip() if result else None
        except Exception:
            return None
    
    async def _extract_key_points(self, summaries: str, topic: str, lang: str) -> Optional[List[str]]:
        """Extract key points from summaries."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", KEY_POINTS_SYSTEM.format(language_instruction=lang)),
            ("user", KEY_POINTS_USER)
        ])
        chain = prompt | self._llm | self._parser
        try:
            result = await chain.ainvoke({"topic": topic, "summaries": summaries})
            return self._parse_key_points(result) if result else None
        except Exception:
            return None
    
    def _parse_key_points(self, text: str) -> Optional[List[str]]:
        """Parse bullet points from LLM response."""
        points = []
        for line in text.strip().split("\n"):
            line = line.strip()
            for prefix in ("•", "-", "*"):
                if line.startswith(prefix):
                    points.append(line[1:].strip())
                    break
            else:
                if line and line[0].isdigit() and "." in line:
                    parts = line.split(".", 1)
                    if len(parts) > 1:
                        points.append(parts[1].strip())
        return points if points else None
    
    async def _generate_comparison(self, summaries: str, topic: str, lang: str) -> Optional[str]:
        """Generate source comparison section."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", COMPARISON_SYSTEM.format(language_instruction=lang)),
            ("user", COMPARISON_USER)
        ])
        chain = prompt | self._llm | self._parser
        try:
            result = await chain.ainvoke({"topic": topic, "summaries": summaries})
            return result.strip() if result else None
        except Exception:
            return None
