import streamlit as st
from datetime import datetime
from file_handler import open_file_location
import logging

logger = logging.getLogger(__name__)


def show_export_ui(conversations, conversation_df):
    """Handle the export UI and functionality"""
    st.subheader("Select Conversation to Export")

    # Show stats
    total_messages = sum(conv["count"] for conv in conversations.values())
    st.write(
        f"Found {len(conversations):,} conversations with {total_messages:,} total messages"
    )

    # Conversation selection
    contact_list = conversation_df["contact"].tolist()
    selected = st.selectbox(
        "Choose conversation",
        contact_list,
        format_func=lambda x: x.split("(")[0].strip(),
    )

    if not selected:
        return

    # Get phone number and stats
    phone = conversation_df[conversation_df["contact"] == selected][
        "phone"
    ].iloc[0]
    stats = conversations[phone]

    # Show conversation stats
    st.write(
        f"Selected conversation: {stats['count']:,} messages "
        f"({stats['sent']:,} sent, {stats['received']:,} received)"
    )

    # Date range selection
    st.subheader("Select Date Range")
    start_ts = stats["first_date"]
    end_ts = stats["last_date"]

    st.write(
        f"Conversation spans from "
        f"{datetime.fromtimestamp(start_ts / 1000).strftime('%B %d, %Y')} to "
        f"{datetime.fromtimestamp(end_ts / 1000).strftime('%B %d, %Y')}"
    )

    # Date inputs
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start date",
            value=datetime.fromtimestamp(start_ts / 1000).date(),
            min_value=datetime.fromtimestamp(start_ts / 1000).date(),
            max_value=datetime.fromtimestamp(end_ts / 1000).date(),
        )
    with col2:
        end_date = st.date_input(
            "End date",
            value=datetime.fromtimestamp(end_ts / 1000).date(),
            min_value=datetime.fromtimestamp(start_ts / 1000).date(),
            max_value=datetime.fromtimestamp(end_ts / 1000).date(),
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

    # Export filename
    safe_phone = "".join(c if c.isalnum() else "_" for c in phone)
    default_filename = (
        f"conversation_{safe_phone}_{start_date}_{end_date}.{output_format}"
    )
    export_path = st.text_input("Export filename", value=default_filename)

    # Export button and handling
    if st.button("Export Conversation"):
        try:
            with st.spinner("Exporting..."):
                output_path = st.session_state.analyzer.export_conversation(
                    phone,
                    start_date,
                    end_date,
                    output_format,
                    output_path=export_path,
                )
                st.success(f"Exported to: {output_path}")
                logger.info(
                    f"Successfully exported conversation to {output_path}"
                )

                # Add button to open export location
                if st.button("Show Export Location"):
                    open_file_location(output_path)

        except Exception as e:
            logger.error(f"Export failed: {str(e)}", exc_info=True)
            st.error(f"Failed to export: {str(e)}")
