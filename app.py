# app.py
import streamlit as st
from pathlib import Path
from ui.instructions import show_instructions
from ui.charts import create_conversation_chart
from conversation import ConversationAnalyzer
from file_handler import find_sms_backups, validate_file, open_file_location
from logging_config import setup_logging
import platform
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def main():
    # Set up logging
    log_file = setup_logging()
    logger.info("Starting SMS Slicer application")
    st.title("SMS Slicer")
    st.caption("Created by Max Ghenis (mghenis@gmail.com)")

    # Show instructions
    show_instructions()

    # File selection
    if "file_path" not in st.session_state:
        st.session_state.file_path = None

    # Look for backup files in Downloads
    backup_files = find_sms_backups()

    col1, col2 = st.columns([2, 1])
    with col1:
        if backup_files:
            # Show dropdown of found backup files
            file_options = {str(f): f.name for f in backup_files}
            selected_file = st.selectbox(
                "Select SMS backup file",
                options=list(file_options.keys()),
                format_func=lambda x: file_options[x],
                help="Recent SMS backup files found in Downloads",
            )
            st.session_state.file_path = selected_file
        else:
            # Fallback to manual path input
            st.session_state.file_path = st.text_input(
                "XML file path",
                value=st.session_state.file_path or "",
                placeholder="/path/to/sms_backup.xml",
            )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing to align with input
        if st.button(
            "Show in Finder"
            if platform.system() == "Darwin"
            else "Show in Explorer"
        ):
            if st.session_state.file_path:
                open_file_location(st.session_state.file_path)

    if st.session_state.file_path:
        valid, result = validate_file(st.session_state.file_path)
        if not valid:
            st.error(result)
            return

        # Initialize analysis
        if "analyzer" not in st.session_state:
            st.session_state.analyzer = ConversationAnalyzer(result)

        # Create placeholders for dynamic updates
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        chart_container = st.empty()
        export_container = st.empty()

        try:
            # Process conversations
            def update_progress(progress, speed, eta, conversations):
                try:
                    progress_bar.progress(float(progress))
                    status_msg = (
                        f"Processing... {speed:.1f} MB/s, {eta:.0f}s remaining"
                    )
                    status_text.text(status_msg)
                    logger.debug(f"Progress update: {status_msg}")
                except Exception as e:
                    logger.error(f"Error updating progress: {str(e)}")

                # Update chart
                with chart_container:
                    conversation_df = create_conversation_chart(
                        conversations, None
                    )
                    if conversation_df is not None:
                        st.session_state.conversation_df = conversation_df

            final_conversations = (
                st.session_state.analyzer.stream_conversations(update_progress)
            )
            logger.info("Processing complete, showing selection UI")

            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

            # Show conversation selection
            st.subheader("Select Conversation to Export")
            if st.session_state.conversation_df is not None:
                # Show stats
                total_messages = sum(
                    conv["count"] for conv in final_conversations.values()
                )
                st.write(
                    f"Found {len(final_conversations):,} conversations with {total_messages:,} total messages"
                )

                # Conversation selection
                contact_list = st.session_state.conversation_df[
                    "contact"
                ].tolist()
                selected = st.selectbox(
                    "Choose conversation",
                    contact_list,
                    format_func=lambda x: x.split("(")[
                        0
                    ].strip(),  # Show just the name part
                )

                if selected:
                    # Get phone number from selection
                    phone = st.session_state.conversation_df[
                        st.session_state.conversation_df["contact"] == selected
                    ]["phone"].iloc[0]

                    # Show conversation stats
                    stats = final_conversations[phone]
                    st.write(
                        f"Selected conversation: {stats['count']:,} messages "
                        f"({stats['sent']:,} sent, {stats['received']:,} received)"
                    )

                    # Date range selection
                    st.subheader("Select Date Range")
                    start_ts = stats["first_date"]
                    end_ts = stats["last_date"]

                    # Show full date range
                    st.write(
                        f"Conversation spans from "
                        f"{datetime.fromtimestamp(start_ts / 1000).strftime('%B %d, %Y')} to "
                        f"{datetime.fromtimestamp(end_ts / 1000).strftime('%B %d, %Y')}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        start_date = st.date_input(
                            "Start date",
                            value=datetime.fromtimestamp(
                                start_ts / 1000
                            ).date(),
                            min_value=datetime.fromtimestamp(
                                start_ts / 1000
                            ).date(),
                            max_value=datetime.fromtimestamp(
                                end_ts / 1000
                            ).date(),
                        )
                    with col2:
                        end_date = st.date_input(
                            "End date",
                            value=datetime.fromtimestamp(end_ts / 1000).date(),
                            min_value=datetime.fromtimestamp(
                                start_ts / 1000
                            ).date(),
                            max_value=datetime.fromtimestamp(
                                end_ts / 1000
                            ).date(),
                        )

                    # Export options
                    st.subheader("Export Options")
                    format_col, button_col = st.columns([1, 2])
                    with format_col:
                        output_format = st.radio(
                            "Format",
                            ["txt", "csv"],
                            help="TXT: Human readable\nCSV: Spreadsheet compatible",
                        )
                    with button_col:
                        if st.button("Export Conversation"):
                            try:
                                with st.spinner("Exporting..."):
                                    output_path = st.session_state.analyzer.export_conversation(
                                        phone,
                                        start_date,
                                        end_date,
                                        output_format,
                                    )
                                    st.success(f"Exported to: {output_path}")
                                    logger.info(
                                        f"Successfully exported conversation to {output_path}"
                                    )
                            except Exception as e:
                                logger.error(
                                    f"Export failed: {str(e)}", exc_info=True
                                )
                                st.error(f"Failed to export: {str(e)}")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")


if __name__ == "__main__":
    main()
