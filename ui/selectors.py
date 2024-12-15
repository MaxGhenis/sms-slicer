import streamlit as st
from datetime import datetime


def show_conversation_selector(conversations_df):
    """Show selector for conversations with message counts"""
    if conversations_df is None or conversations_df.empty:
        return None

    return st.selectbox(
        "Select conversation to export",
        conversations_df["contact"].tolist(),
        format_func=lambda x: x,  # Already formatted in DataFrame
    )


def show_date_range_selector(start_ts, end_ts):
    """Show date range selector with conversation bounds"""
    start_date = datetime.fromtimestamp(start_ts / 1000).date()
    end_date = datetime.fromtimestamp(end_ts / 1000).date()

    col1, col2 = st.columns(2)
    with col1:
        selected_start = st.date_input(
            "Start date",
            value=start_date,
            min_value=start_date,
            max_value=end_date,
        )
    with col2:
        selected_end = st.date_input(
            "End date",
            value=end_date,
            min_value=selected_start,
            max_value=end_date,
        )

    return selected_start, selected_end


def show_export_options():
    """Show export format selection and button"""
    format_col, button_col = st.columns([1, 2])
    with format_col:
        output_format = st.radio(
            "Export format",
            ["txt", "csv"],
            help="TXT: Human readable format\nCSV: Spreadsheet compatible",
        )
    with button_col:
        export_clicked = st.button(
            "Export Conversation", help="Save selected conversation to file"
        )

    return output_format, export_clicked
