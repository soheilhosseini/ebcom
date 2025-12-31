"""
Streamlit UI for the research feature.
"""

import asyncio
import streamlit as st

from src.shared.config import settings
from src.features.research.services import create_research_service
from src.features.research.infrastructure.formatting import MarkdownJsonFormatter
from src.features.research.domain import (
    ProgressEvent,
    OutputFormat,
    ResearchError,
)
from src.features.research.constants import (
    UI_PAGE_TITLE,
    UI_PAGE_ICON,
    UI_POWERED_BY,
    PROGRESS_MAP,
    PROGRESS_FETCHING_BASE,
    PROGRESS_SUMMARIZING_BASE,
    PROGRESS_STEP_RANGE,
)


def configure_page():
    """Configure Streamlit page."""
    st.set_page_config(
        page_title=UI_PAGE_TITLE,
        page_icon=UI_PAGE_ICON,
        layout="centered"
    )
    st.markdown("""
    <style>
        .stProgress > div > div > div > div { background-color: #4CAF50; }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render page header."""
    st.title("🔍 Research AI Assistant")
    st.markdown(
        "Enter a research topic in **any language** "
        "to get a comprehensive summary with citations."
    )


def init_session_state():
    """Initialize session state."""
    if "report" not in st.session_state:
        st.session_state.report = None
    if "format" not in st.session_state:
        st.session_state.format = OutputFormat.MARKDOWN.value


def render_form():
    """Render input form."""
    with st.form("research_form"):
        topic = st.text_input(
            "Research Topic",
            placeholder="Enter your research topic...",
            help="Supports any language"
        )
        
        num_sources = st.slider(
            "Number of Sources",
            min_value=settings.research.min_sources,
            max_value=settings.research.max_sources,
            value=settings.research.default_sources
        )
        
        submitted = st.form_submit_button("🚀 Start Research", use_container_width=True)
        return submitted, topic, num_sources


def create_progress_callback(progress_bar, status):
    """Create progress callback."""
    async def callback(event: ProgressEvent):
        if event.step in ("fetching", "summarizing"):
            base = PROGRESS_FETCHING_BASE if event.step == "fetching" else PROGRESS_SUMMARIZING_BASE
            progress = base + PROGRESS_STEP_RANGE * (event.current or 1) / (event.total or 1)
        else:
            progress = PROGRESS_MAP.get(event.step, 0)
        progress_bar.progress(progress)
        status.info(f"📊 {event.message}")
    
    return callback


async def execute_research(topic, num_sources, progress_bar, status):
    """Execute research."""
    service = create_research_service()
    callback = create_progress_callback(progress_bar, status)
    return await service.research(
        topic=topic,
        num_sources=num_sources,
        progress_callback=callback
    )


def render_results():
    """Render research results."""
    if not st.session_state.report:
        return
    
    st.divider()
    st.subheader("📄 Research Results")
    
    # Format selector
    output_format = st.radio(
        "Output Format",
        options=[OutputFormat.MARKDOWN.value, OutputFormat.JSON.value],
        format_func=lambda x: "Markdown" if x == "markdown" else "JSON",
        horizontal=True,
        key="format_selector"
    )
    st.session_state.format = output_format
    
    # Format the report
    formatter = MarkdownJsonFormatter()
    content = formatter.format(st.session_state.report, output_format)
    
    # Download button
    ext = "md" if output_format == "markdown" else "json"
    mime = "text/markdown" if ext == "md" else "application/json"
    st.download_button(
        "📥 Download",
        data=content,
        file_name=f"research.{ext}",
        mime=mime,
        use_container_width=True
    )
    
    # Display content
    if output_format == "markdown":
        st.markdown(content)
    else:
        st.code(content, language="json")
    
    with st.expander("📝 View Raw Content"):
        lang = "markdown" if output_format == "markdown" else "json"
        st.code(content, language=lang)


def handle_submission(submitted, topic, num_sources):
    """Handle form submission."""
    if not submitted:
        return
    
    if not topic or not topic.strip():
        st.error("⚠️ Please enter a research topic")
        return
    
    progress_bar = st.empty().progress(0)
    status = st.empty()
    
    try:
        with st.spinner("Researching..."):
            result = asyncio.run(execute_research(
                topic.strip(), num_sources, progress_bar, status
            ))
            st.session_state.report = result.report
            status.success("✅ Research complete!")
    except ResearchError as e:
        status.error(f"❌ {e.message}")
        st.session_state.report = None
    except Exception:
        status.error("❌ An unexpected error occurred. Please try again.")
        st.session_state.report = None


def run_streamlit_app():
    """Main entry point for Streamlit app."""
    configure_page()
    render_header()
    init_session_state()
    
    submitted, topic, num_sources = render_form()
    handle_submission(submitted, topic, num_sources)
    
    render_results()
    
    st.divider()
    st.caption(UI_POWERED_BY)


if __name__ == "__main__":
    run_streamlit_app()
