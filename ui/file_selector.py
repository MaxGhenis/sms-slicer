import streamlit as st
from pathlib import Path
import platform
from file_handler import find_sms_backups, open_file_location, validate_file
from sample_data import generate_sample_data


def show_file_selector():
    """Handle file selection UI including sample data option"""
    # Initialize session state
    if "file_path" not in st.session_state:
        st.session_state.file_path = None

    # Add option to use sample data
    use_sample = st.checkbox(
        "Use sample data", help="Use included sample_backup.xml for testing"
    )

    if use_sample:
        sample_path = Path("sample_data/sample_backup.xml")
        if sample_path.exists():
            st.session_state.file_path = str(sample_path)
            st.info("Using sample_backup.xml")
        else:
            st.error(
                "sample_backup.xml not found. Please run sample_data/generate_sample_data.py first."
            )
            if st.button("Generate Sample Data"):
                try:
                    generate_sample_data.create_sample_backup()
                    st.success(
                        "Sample data generated! Please reload the page."
                    )
                    st.session_state.file_path = str(sample_path)
                except Exception as e:
                    st.error(f"Error generating sample data: {str(e)}")
    else:
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

    # Validate and return file path
    if st.session_state.file_path:
        valid, result = validate_file(st.session_state.file_path)
        if not valid:
            st.error(result)
            return None
        return result
    return None
