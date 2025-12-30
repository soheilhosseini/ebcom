"""
Reasoning Chain module for the Research AI Assistant.

This module provides LangChain-based multi-step reasoning to combine
source summaries and generate comprehensive final reports with
summary, key points, source comparison, and citations.
"""

import os
from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from models import SourceSummary, FinalReport, Citation


class ReasoningChain:
    """
    LangChain-based reasoning chain for generating final research reports.
    
    Implements a multi-step workflow:
    1. Combine all source summaries
    2. Identify key points across sources
    3. Compare and contrast sources
    4. Generate comprehensive final report
    """
    
    MODEL = "gpt-4o"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the reasoning chain with OpenAI LLM.
        
        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(
            model=self.MODEL,
            api_key=self.api_key,
            temperature=0.3
        )
        self.output_parser = StrOutputParser()

    async def generate_report(
        self,
        summaries: List[SourceSummary],
        topic: str,
        language: str
    ) -> Optional[FinalReport]:
        """
        Generate final report with reasoning from source summaries.
        
        Args:
            summaries: List of source summaries to analyze
            topic: Original research topic
            language: Output language code ("en" or "fa")
            
        Returns:
            FinalReport with summary, key_points, comparison, citations,
            or None if generation fails.
        """
        if not summaries:
            return None
        
        try:
            # Build citations from summaries
            citations = self._build_citations(summaries)
            
            # Format summaries for the prompt
            formatted_summaries = self._format_summaries(summaries)
            
            # Get language instruction
            lang_instruction = self._get_language_instruction(language)
            
            # Step 1: Generate main summary
            main_summary = await self._generate_main_summary(
                formatted_summaries, topic, lang_instruction
            )
            
            # Step 2: Extract key points
            key_points = await self._extract_key_points(
                formatted_summaries, topic, lang_instruction
            )
            
            # Step 3: Generate source comparison
            comparison = await self._generate_comparison(
                formatted_summaries, topic, lang_instruction
            )
            
            if not main_summary or not key_points or not comparison:
                return None
            
            return FinalReport(
                summary=main_summary,
                key_points=key_points,
                comparison=comparison,
                citations=citations,
                language=language
            )
            
        except Exception:
            # Handle any errors gracefully
            return None

    def _build_citations(self, summaries: List[SourceSummary]) -> List[Citation]:
        """
        Build citation list from source summaries.
        
        Args:
            summaries: List of source summaries
            
        Returns:
            List of Citation objects with sequential numbering
        """
        return [
            Citation(
                number=s.source_number,
                title=s.title,
                url=s.url
            )
            for s in summaries
        ]
    
    def _format_summaries(self, summaries: List[SourceSummary]) -> str:
        """
        Format summaries for inclusion in prompts.
        
        Args:
            summaries: List of source summaries
            
        Returns:
            Formatted string with all summaries
        """
        formatted = []
        for s in summaries:
            formatted.append(
                f"[{s.source_number}] {s.title}\n"
                f"URL: {s.url}\n"
                f"Summary: {s.summary}\n"
            )
        return "\n".join(formatted)
    
    def _get_language_instruction(self, language: str) -> str:
        """
        Get language-specific instruction for prompts.
        
        Args:
            language: Language code ("en" or "fa")
            
        Returns:
            Instruction string for the specified language
        """
        if language == "fa":
            return "You MUST write your entire response in Persian (Farsi). Do not use English."
        return "You MUST write your entire response in English. Do not use other languages."

    async def _generate_main_summary(
        self,
        formatted_summaries: str,
        topic: str,
        lang_instruction: str
    ) -> Optional[str]:
        """
        Generate the main summary section combining all sources.
        
        Args:
            formatted_summaries: Formatted source summaries
            topic: Research topic
            lang_instruction: Language instruction
            
        Returns:
            Main summary text or None if failed
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a research analyst creating comprehensive summaries.
{lang_instruction}
Your task is to synthesize multiple source summaries into a unified, coherent summary.
Focus on the main findings and insights about the topic.
Use citation numbers [1], [2], etc. when referencing specific sources."""),
            ("user", """Research Topic: {topic}

Source Summaries:
{summaries}

Create a comprehensive summary (2-3 paragraphs) that synthesizes the key information from all sources about this topic. Include citation numbers when referencing specific sources.""")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        try:
            result = await chain.ainvoke({
                "topic": topic,
                "summaries": formatted_summaries
            })
            return result.strip() if result else None
        except Exception:
            return None

    async def _extract_key_points(
        self,
        formatted_summaries: str,
        topic: str,
        lang_instruction: str
    ) -> Optional[List[str]]:
        """
        Extract key points from all source summaries.
        
        Args:
            formatted_summaries: Formatted source summaries
            topic: Research topic
            lang_instruction: Language instruction
            
        Returns:
            List of key points or None if failed
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a research analyst identifying key points.
{lang_instruction}
Your task is to extract the most important points from the research summaries.
Each point should be a complete, standalone statement.
Include citation numbers [1], [2], etc. when a point comes from a specific source.
Return exactly 5-7 key points, one per line, starting with a bullet point (•)."""),
            ("user", """Research Topic: {topic}

Source Summaries:
{summaries}

Extract 5-7 key points from these sources. Each point should be on its own line starting with •""")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        try:
            result = await chain.ainvoke({
                "topic": topic,
                "summaries": formatted_summaries
            })
            
            if not result:
                return None
            
            # Parse bullet points from the response
            lines = result.strip().split('\n')
            key_points = []
            for line in lines:
                line = line.strip()
                if line.startswith('•'):
                    key_points.append(line[1:].strip())
                elif line.startswith('-'):
                    key_points.append(line[1:].strip())
                elif line.startswith('*'):
                    key_points.append(line[1:].strip())
                elif line and not line[0].isdigit():
                    # Include lines that don't start with numbers
                    key_points.append(line)
                elif line and line[0].isdigit() and '.' in line:
                    # Handle numbered lists like "1. Point"
                    parts = line.split('.', 1)
                    if len(parts) > 1:
                        key_points.append(parts[1].strip())
            
            return key_points if key_points else None
            
        except Exception:
            return None

    async def _generate_comparison(
        self,
        formatted_summaries: str,
        topic: str,
        lang_instruction: str
    ) -> Optional[str]:
        """
        Generate source comparison section.
        
        Args:
            formatted_summaries: Formatted source summaries
            topic: Research topic
            lang_instruction: Language instruction
            
        Returns:
            Comparison text or None if failed
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a research analyst comparing multiple sources.
{lang_instruction}
Your task is to compare and contrast the different sources.
Identify areas of agreement, disagreement, and unique perspectives.
Use citation numbers [1], [2], etc. when referencing specific sources."""),
            ("user", """Research Topic: {topic}

Source Summaries:
{summaries}

Write a comparison section (1-2 paragraphs) that analyzes how these sources relate to each other. Highlight agreements, disagreements, and unique contributions from each source.""")
        ])
        
        chain = prompt | self.llm | self.output_parser
        
        try:
            result = await chain.ainvoke({
                "topic": topic,
                "summaries": formatted_summaries
            })
            return result.strip() if result else None
        except Exception:
            return None
