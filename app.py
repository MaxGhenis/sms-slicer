import streamlit as st
from logging_config import setup_logging
from ui.instructions import show_instructions
from ui.file_selector import show_file_selector
from ui.processor import show_processor
from ui.export import show_export_ui
import logging

logger = logging.getLogger(__name__)


def main():
    # Set up logging
    log_file = setup_logging()
    logger.info("Starting SMS Slicer application")

    # Main UI
    st.title("SMS Slicer")
    st.caption("Created by Max Ghenis (mghenis@gmail.com)")
    show_instructions()

    # File selection
    file_path = show_file_selector()
    if not file_path:
        return

    # Processing
    conversations = show_processor(file_path)
    if not conversations:
        return

    # Export UI
    if hasattr(st.session_state, "conversation_df"):
        show_export_ui(conversations, st.session_state.conversation_df)


if __name__ == "__main__":
    main()
