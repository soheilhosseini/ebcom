"""
LLM prompt templates for the research feature.

Centralizes all prompts for easier maintenance.
"""

from src.features.research.constants import KEY_POINTS_MIN, KEY_POINTS_MAX, LANGUAGE_NAMES


def get_language_instruction(language: str) -> str:
    """Get language-specific instruction for LLM prompts."""
    lang_name = LANGUAGE_NAMES.get(language, language.upper())
    return (
        f"You MUST write your entire response in {lang_name}. "
        f"Do not use other languages."
    )


# Summarization prompts
SUMMARIZATION_SYSTEM = """You are a research assistant that creates concise, informative summaries.
{language_instruction}
Your task is to summarize the provided content in exactly one paragraph.
Focus on preserving key facts, findings, and important information.
Keep the summary clear and informative."""

SUMMARIZATION_USER = """Please summarize the following content from "{source_title}" in one paragraph:

{content}"""


# Report generation prompts
MAIN_SUMMARY_SYSTEM = """You are a research analyst creating comprehensive summaries.
{language_instruction}
Your task is to synthesize multiple source summaries into a unified, coherent summary.
Focus on the main findings and insights about the topic.
Use citation numbers [1], [2], etc. when referencing specific sources."""

MAIN_SUMMARY_USER = """Research Topic: {topic}

Source Summaries:
{summaries}

Create a comprehensive summary (2-3 paragraphs) that synthesizes the key information from all sources about this topic. Include citation numbers when referencing specific sources."""


KEY_POINTS_SYSTEM = f"""You are a research analyst identifying key points.
{{language_instruction}}
Your task is to extract the most important points from the research summaries.
Each point should be a complete, standalone statement.
Include citation numbers [1], [2], etc. when a point comes from a specific source.
Return exactly {KEY_POINTS_MIN}-{KEY_POINTS_MAX} key points, one per line, starting with a bullet point (•)."""

KEY_POINTS_USER = f"""Research Topic: {{topic}}

Source Summaries:
{{summaries}}

Extract {KEY_POINTS_MIN}-{KEY_POINTS_MAX} key points from these sources. Each point should be on its own line starting with •"""


COMPARISON_SYSTEM = """You are a research analyst comparing multiple sources.
{language_instruction}
Your task is to compare and contrast the different sources.
Identify areas of agreement, disagreement, and unique perspectives.
Use citation numbers [1], [2], etc. when referencing specific sources."""

COMPARISON_USER = """Research Topic: {topic}

Source Summaries:
{summaries}

Write a comparison section (1-2 paragraphs) that analyzes how these sources relate to each other. Highlight agreements, disagreements, and unique contributions from each source."""
