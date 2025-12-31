"""
Streamlit frontend for the Research AI Assistant.

This provides a pure Python UI alternative to the React frontend.
Run with: streamlit run streamlit_app.py
"""

import asyncio
import streamlit as st
from dotenv import load_dotenv

from research_agent import ResearchAgent, ResearchError
from models import ProgressEvent

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Research AI Assistant",
    page_icon="🔍",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🔍 Research AI Assistant")
st.markdown("Enter a research topic in **English** or **Persian** to get a comprehensive summary with citations.")

# Initialize session state
if "research_result" not in st.session_state:
    st.session_state.research_result = None
if "output_format" not in st.session_state:
    st.session_state.output_format = "markdown"
if "is_researching" not in st.session_state:
    st.session_state.is_researching = False

# Input form
with st.form("research_form"):
    topic = st.text_input(
        "Research Topic",
        placeholder="Enter your research topic...",
        help="Supports both English and Persian"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_sources = st.slider(
            "Number of Sources",
            min_value=3,
            max_value=10,
            value=5,
            help="More sources = more comprehensive but slower"
        )
    
    with col2:
        output_format = st.radio(
            "Output Format",
            options=["markdown", "json"],
            format_func=lambda x: "Markdown" if x == "markdown" else "JSON",
            horizontal=True
        )
    
    submitted = st.form_submit_button("🚀 Start Research", use_container_width=True)


async def run_research(topic: str, num_sources: int, output_format: str, progress_placeholder, status_placeholder):
    """Run the research workflow with progress updates."""
    agent = ResearchAgent()
    
    progress_messages = []
    progress_bar = progress_placeholder.progress(0)
    
    async def progress_callback(event: ProgressEvent):
        """Handle progress events from the research agent."""
        progress_messages.append(event.message)
        
        # Update progress bar based on step
        progress_map = {
            "searching": 0.1,
            "found": 0.15,
            "fetching": 0.15 + (0.3 * (event.current or 1) / (event.total or 1)),
            "summarizing": 0.45 + (0.3 * (event.current or 1) / (event.total or 1)),
            "analyzing": 0.8,
            "finalizing": 0.9,
            "complete": 1.0
        }
        
        progress = progress_map.get(event.step, 0)
        progress_bar.progress(progress)
        status_placeholder.info(f"📊 {event.message}")
    
    result = await agent.research(
        topic=topic,
        num_sources=num_sources,
        output_format=output_format,
        progress_callback=progress_callback
    )
    
    return result


# Handle form submission
if submitted:
    if not topic or not topic.strip():
        st.error("⚠️ Please enter a research topic")
    else:
        st.session_state.output_format = output_format
        
        # Progress display
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            with st.spinner("Researching..."):
                result = asyncio.run(run_research(
                    topic=topic.strip(),
                    num_sources=num_sources,
                    output_format=output_format,
                    progress_placeholder=progress_placeholder,
                    status_placeholder=status_placeholder
                ))
                
                st.session_state.research_result = result
                status_placeholder.success("✅ Research complete!")
                
        except ResearchError as e:
            status_placeholder.error(f"❌ {e.message}")
            st.session_state.research_result = None
        except Exception as e:
            status_placeholder.error("❌ An unexpected error occurred. Please try again.")
            st.session_state.research_result = None

# Display results
if st.session_state.research_result:
    st.divider()
    st.subheader("📄 Research Results")
    
    # Export buttons
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Download",
            data=st.session_state.research_result,
            file_name=f"research.{'md' if st.session_state.output_format == 'markdown' else 'json'}",
            mime="text/markdown" if st.session_state.output_format == "markdown" else "application/json",
            use_container_width=True
        )
    
    with col2:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.toast("Copied to clipboard!", icon="✅")
            # Note: Actual clipboard copy requires JavaScript, showing code block instead
    
    # Display content
    if st.session_state.output_format == "markdown":
        st.markdown(st.session_state.research_result)
    else:
        st.code(st.session_state.research_result, language="json")
    
    # Show raw content in expander
    with st.expander("📝 View Raw Content"):
        st.code(st.session_state.research_result, language="markdown" if st.session_state.output_format == "markdown" else "json")

# Footer
st.divider()
st.caption("Built with Streamlit • Powered by GPT-4o • Search by DuckDuckGo")
