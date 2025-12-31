"""
Application entry point.

This module provides the main entry point for running the application.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.features.research.presentation import run_streamlit_app


def main():
    """Run the application."""
    run_streamlit_app()


if __name__ == "__main__":
    main()
