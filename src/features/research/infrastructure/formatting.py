"""
Output formatting implementation.
"""

import json

from src.features.research.domain.models import FinalReport
from src.features.research.domain.enums import OutputFormat


class MarkdownJsonFormatter:
    """Formats reports as Markdown or JSON."""
    
    def format(self, report: FinalReport, format_type: str) -> str:
        """Format a report into the specified format."""
        if format_type == OutputFormat.JSON.value:
            return self._to_json(report)
        return self._to_markdown(report)
    
    def _to_json(self, report: FinalReport) -> str:
        """Format as JSON."""
        return json.dumps({
            "summary": report.summary,
            "key_points": report.key_points,
            "comparison": report.comparison,
            "citations": [
                {"number": c.number, "title": c.title, "url": c.url}
                for c in report.citations
            ],
            "language": report.language
        }, ensure_ascii=False, indent=2)
    
    def _to_markdown(self, report: FinalReport) -> str:
        """Format as Markdown."""
        sections = [
            f"# Summary\n\n{report.summary}\n",
            "# Key Points\n\n" + "\n".join(f"- {p}" for p in report.key_points) + "\n",
            f"# Comparison\n\n{report.comparison}\n",
            "# Citations\n\n" + "\n".join(
                f"[{c.number}] {c.title} - {c.url}" for c in report.citations
            )
        ]
        return "\n".join(sections)
