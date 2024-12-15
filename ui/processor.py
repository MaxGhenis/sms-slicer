import streamlit as st
from conversation import ConversationAnalyzer
import logging

logger = logging.getLogger(__name__)


def show_processor(file_path):
    """Handle the file processing UI and logic"""
    # Initialize session state for processing
    if "processing_started" not in st.session_state:
        st.session_state.processing_started = False
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = None

    # Show process button if not started
    if not st.session_state.processing_started:
        if st.button("Process SMS Backup", key="process_button"):
            st.session_state.processing_started = True
            st.session_state.analyzer = ConversationAnalyzer(file_path)
            st.rerun()
        return None

    # If processing has started, show progress
    if st.session_state.analyzer is None:
        st.session_state.analyzer = ConversationAnalyzer(file_path)

    progress_bar = st.progress(0.0)
    status_text = st.empty()
    chart_container = st.empty()

    def update_progress(progress, speed, eta, conversations):
        try:
            progress_bar.progress(float(progress))
            status_msg = (
                f"Processing... {speed:.1f} MB/s, {eta:.0f}s remaining"
            )
            status_text.text(status_msg)
            logger.debug(f"Progress update: {status_msg}")
        except Exception as e:
            logger.error(f"Error updating progress: {str(e)}", exc_info=True)

        # Update chart
        with chart_container:
            from ui.charts import create_conversation_chart

            conversation_df = create_conversation_chart(conversations, None)
            if conversation_df is not None:
                st.session_state.conversation_df = conversation_df

    try:
        final_conversations = st.session_state.analyzer.stream_conversations(
            update_progress
        )
        progress_bar.empty()
        status_text.empty()
        return final_conversations
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        logger.error(f"Processing error: {str(e)}", exc_info=True)
        return None
