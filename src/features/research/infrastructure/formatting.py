"""
Output formatting implementation.
"""

import json

from src.features.research.domain.models import FinalReport
from src.features.research.domain.enums import OutputFormat


# Localized section titles
SECTION_TITLES = {
    "en": {
        "summary": "Summary",
        "key_points": "Key Points",
        "comparison": "Comparison",
        "citations": "Citations"
    },
    "fa": {
        "summary": "خلاصه",
        "key_points": "نکات کلیدی",
        "comparison": "مقایسه",
        "citations": "منابع"
    },
    "ar": {
        "summary": "ملخص",
        "key_points": "النقاط الرئيسية",
        "comparison": "المقارنة",
        "citations": "المراجع"
    },
    "ja": {
        "summary": "要約",
        "key_points": "重要ポイント",
        "comparison": "比較",
        "citations": "引用"
    },
    "zh-cn": {
        "summary": "摘要",
        "key_points": "要点",
        "comparison": "比较",
        "citations": "引用"
    },
    "de": {
        "summary": "Zusammenfassung",
        "key_points": "Kernpunkte",
        "comparison": "Vergleich",
        "citations": "Quellen"
    },
    "fr": {
        "summary": "Résumé",
        "key_points": "Points Clés",
        "comparison": "Comparaison",
        "citations": "Citations"
    },
    "es": {
        "summary": "Resumen",
        "key_points": "Puntos Clave",
        "comparison": "Comparación",
        "citations": "Citas"
    },
}


def get_titles(language: str) -> dict:
    """Get section titles for the given language."""
    return SECTION_TITLES.get(language, SECTION_TITLES["en"])


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
        """Format as Markdown with localized titles."""
        titles = get_titles(report.language)
        sections = [
            f"# {titles['summary']}\n\n{report.summary}\n",
            f"# {titles['key_points']}\n\n" + "\n".join(f"- {p}" for p in report.key_points) + "\n",
            f"# {titles['comparison']}\n\n{report.comparison}\n",
            f"# {titles['citations']}\n\n" + "\n\n".join(
                f"[{c.number}] {c.title} - {c.url}" for c in report.citations
            )
        ]
        return "\n".join(sections)
