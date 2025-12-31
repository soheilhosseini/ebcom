"""
Constants for the research feature.

Centralizes all hardcoded values for easier maintenance.
"""

# HTTP Client
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.124 Safari/537.36"
)

# Content Processing
TRUNCATION_ELLIPSIS = "[...]"

# Report Generation
KEY_POINTS_MIN = 5
KEY_POINTS_MAX = 7

# Language Detection
# Map of language codes to their display names (for common languages)
LANGUAGE_NAMES = {
    "en": "English",
    "fa": "Persian",
    "ar": "Arabic",
    "ja": "Japanese",
    "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)",
    "ko": "Korean",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "ru": "Russian",
    "pt": "Portuguese",
    "it": "Italian",
    "nl": "Dutch",
    "tr": "Turkish",
    "hi": "Hindi",
    "ur": "Urdu",
}

# UI Configuration
UI_PAGE_TITLE = "Research AI Assistant"
UI_PAGE_ICON = "🔍"
UI_POWERED_BY = "Built with Streamlit • Powered by GPT-5 Nano • Search by DuckDuckGo"

# Progress Steps Mapping (step -> progress percentage)
PROGRESS_MAP = {
    "searching": 0.1,
    "found": 0.15,
    "analyzing": 0.8,
    "finalizing": 0.9,
    "complete": 1.0,
}

# Progress Base Values
PROGRESS_FETCHING_BASE = 0.15
PROGRESS_SUMMARIZING_BASE = 0.45
PROGRESS_STEP_RANGE = 0.3
