"""
Output formatter for the Research AI Assistant.

This module provides formatting capabilities to convert FinalReport objects
into JSON or Markdown output formats.
"""

import json
from typing import Literal

from models import FinalReport


class OutputFormatter:
    """Formats research reports as JSON or Markdown."""

    def format(self, report: FinalReport, format_type: Literal["json", "markdown"]) -> str:
        """
        Format report as JSON or Markdown.

        Args:
            report: FinalReport object containing the research results
            format_type: "json" or "markdown"

        Returns:
            Formatted string in the requested format
        """
        if format_type == "json":
            return self._format_json(report)
        else:
            return self._format_markdown(report)

    def _format_json(self, report: FinalReport) -> str:
        """
        Format report as structured JSON.

        Args:
            report: FinalReport object

        Returns:
            JSON string with all required fields
        """
        output = {
            "summary": report.summary,
            "key_points": report.key_points,
            "comparison": report.comparison,
            "citations": [
                {
                    "number": citation.number,
                    "title": citation.title,
                    "url": citation.url
                }
                for citation in report.citations
            ],
            "language": report.language
        }
        return json.dumps(output, ensure_ascii=False, indent=2)

    def _format_markdown(self, report: FinalReport) -> str:
        """
        Format report as Markdown with proper headers and structure.

        Args:
            report: FinalReport object

        Returns:
            Markdown string with sections for Summary, Key Points, Comparison, and Citations
        """
        sections = []

        # Summary section
        sections.append("# Summary\n")
        sections.append(report.summary)
        sections.append("")

        # Key Points section
        sections.append("# Key Points\n")
        for point in report.key_points:
            sections.append(f"- {point}")
        sections.append("")

        # Comparison section
        sections.append("# Comparison\n")
        sections.append(report.comparison)
        sections.append("")

        # Citations section
        sections.append("# Citations\n")
        for citation in report.citations:
            sections.append(f"[{citation.number}] {citation.title} - {citation.url}")

        return "\n".join(sections)
