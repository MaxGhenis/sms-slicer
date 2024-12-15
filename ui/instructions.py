import streamlit as st


def show_instructions():
    with st.expander("Instructions", expanded=True):
        st.markdown(
            """
        ### How to use SMS Slicer
        
        1. **Install SMS Backup & Restore** (Android only)
           * Download from [Google Play Store](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore)
           * Note: iOS version coming soon
        
        2. **Backup your messages**
           * Open SMS Backup & Restore
           * Select "BACKUP"
           * Choose backup location (Google Drive recommended)
           * Wait for backup to complete
        
        3. **Download and slice**
           * Download the backup file from Google Drive to your computer
           * Click "Select File" below to choose the downloaded XML file
           * Select a conversation from the chart
           * Choose your date range and export format
        
        ### Tips
        * Large backups may take a few minutes to process
        * The conversation chart updates every 10 seconds while processing
        * You can select a conversation while processing continues
        """
        )
