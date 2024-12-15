# SMS Slicer

Extract and analyze conversations from Android SMS backups.

## Features

- Process large SMS backup XML files efficiently
- View conversation statistics and message counts
- Export individual conversations as TXT or CSV
- Filter by date range
- Progress tracking for large files

## Installation

```bash
# Clone the repository
git clone https://github.com/MaxGhenis/sms-slicer
cd sms-slicer

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

1. **Create SMS backup**

   - Install [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore) (Android only)
   - Create a backup and save to Google Drive
   - Download the XML file to your computer

2. **Run SMS Slicer**

   ```bash
   streamlit run app.py
   ```

3. **Process your backup**
   - Select the downloaded XML file
   - Click "Process SMS Backup"
   - Wait for processing to complete
   - Select a conversation and date range
   - Export to TXT or CSV

## Development

### Sample Data

For testing or demonstration, you can generate sample SMS backup data:

```bash
python generate_sample_data.py --messages 1000 --contacts 10
```

This will create `sample_backup.xml` with synthetic messages.

### Project Structure

```
sms_slicer/
├── app.py              # Main Streamlit app
├── conversation.py     # Conversation analysis logic
├── file_handler.py     # File path handling
├── logging_config.py   # Logging setup
└── ui/                 # UI components
    ├── charts.py
    ├── instructions.py
    └── selectors.py
```

### Logging

Logs are written to `logs/sms_slicer.log` with DEBUG level details.

## License

MIT License

## Author

Max Ghenis (mghenis@gmail.com)
