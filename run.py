"""
Entry point for running the Research AI Assistant.

Usage:
    python run.py              # Runs the Streamlit app
    python run.py --api        # Runs the FastAPI server
"""

import sys
import subprocess


def run_streamlit():
    """Run the Streamlit application."""
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "src/features/research/presentation/streamlit_ui.py",
        "--server.port=8501"
    ])


def run_fastapi():
    """Run the FastAPI server."""
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--reload",
        "--port=8000"
    ])


def main():
    """Main entry point."""
    if "--api" in sys.argv:
        print("Starting FastAPI server on http://localhost:8000")
        run_fastapi()
    else:
        print("Starting Streamlit app on http://localhost:8501")
        run_streamlit()


if __name__ == "__main__":
    main()
