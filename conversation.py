# conversation.py
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
import time
from pathlib import Path
import streamlit as st
import logging

logger = logging.getLogger(__name__)


class ConversationAnalyzer:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.file_size = self.file_path.stat().st_size
        logger.info(
            f"Initializing analyzer for {file_path} (size: {self.file_size / (1024*1024):.2f} MB)"
        )
        self.conversations = defaultdict(
            lambda: {
                "count": 0,
                "sent": 0,
                "received": 0,
                "contact_name": "(Unknown)",
                "first_date": None,
                "last_date": None,
            }
        )

    def stream_conversations(self, progress_callback):
        """Stream conversation data as it's processed"""
        logger.info("Starting conversation streaming")
        start_time = time.time()
        context = ET.iterparse(self.file_path, events=("end",))
        last_update = time.time()
        update_interval = 1  # Update UI every second
        total_bytes = 0
        messages_processed = 0

        # Process in larger chunks for better performance
        chunk_size = 1000  # Process 1000 messages before checking time
        chunk = []

        try:
            logger.debug("Beginning XML parsing")
            for event, elem in context:
                if elem.tag == "sms":
                    # Process message
                    address = elem.get("address")
                    contact_name = elem.get("contact_name", "")
                    msg_date = int(elem.get("date", 0))
                    msg_type = (
                        "sent" if elem.get("type") == "2" else "received"
                    )

                    # Add to current chunk
                    chunk.append((address, contact_name, msg_date, msg_type))
                    elem_size = len(ET.tostring(elem))
                    total_bytes += elem_size

                    # Process chunk if it's full
                    if len(chunk) >= chunk_size:
                        self._process_chunk(chunk)
                        messages_processed += len(chunk)
                        chunk = []

                        # Update progress based on time interval
                        current_time = time.time()
                        if current_time - last_update >= update_interval:
                            elapsed = current_time - start_time
                            if elapsed > 0:
                                speed = total_bytes / (1024 * 1024 * elapsed)
                                eta = (
                                    (self.file_size - total_bytes)
                                    / (speed * 1024 * 1024)
                                    if speed > 0
                                    else 0
                                )
                                progress = min(
                                    total_bytes / self.file_size, 1.0
                                )
                                logger.debug(
                                    f"Progress: {progress:.1%}, Speed: {speed:.1f} MB/s, "
                                    f"ETA: {eta:.0f}s, Messages: {messages_processed:,}"
                                )
                                progress_callback(
                                    progress,
                                    speed,
                                    eta,
                                    dict(self.conversations),
                                )
                                last_update = current_time

                    elem.clear()

            # Process any remaining messages
            if chunk:
                self._process_chunk(chunk)

            # Final update
            progress_callback(1.0, 0, 0, dict(self.conversations))
            logger.info(
                f"Processing complete. Found {len(self.conversations)} conversations, "
                f"processed {messages_processed:,} messages"
            )
            return dict(self.conversations)

        except Exception as e:
            logger.error(
                f"Error while processing XML: {str(e)}", exc_info=True
            )
            raise e

    def _process_chunk(self, chunk):
        """Process a chunk of messages efficiently"""
        for address, contact_name, msg_date, msg_type in chunk:
            conv = self.conversations[address]
            conv["count"] += 1
            conv[msg_type] += 1

            # Update contact name if it's not already set
            if not conv["contact_name"] or conv["contact_name"] == "(Unknown)":
                conv["contact_name"] = (
                    contact_name if contact_name else "(Unknown)"
                )

            # Update date range
            if conv["first_date"] is None or msg_date < conv["first_date"]:
                conv["first_date"] = msg_date
            if conv["last_date"] is None or msg_date > conv["last_date"]:
                conv["last_date"] = msg_date

    def export_conversation(
        self,
        phone,
        start_date,
        end_date,
        output_format="txt",
        output_path=None,
    ):
        """Export a specific conversation within date range"""
        start_timestamp = int(
            datetime.combine(start_date, datetime.min.time()).timestamp()
            * 1000
        )
        end_timestamp = int(
            datetime.combine(end_date, datetime.max.time()).timestamp() * 1000
        )

        if output_path is None:
            safe_phone = "".join(c if c.isalnum() else "_" for c in phone)
            output_path = Path(
                f"conversation_{safe_phone}_{start_date}_{end_date}.{output_format}"
            )

        messages = []
        context = ET.iterparse(self.file_path, events=("end",))

        try:
            for event, elem in context:
                if elem.tag == "sms":
                    msg_date = int(elem.get("date", 0))
                    if (
                        elem.get("address") == phone
                        and start_timestamp <= msg_date <= end_timestamp
                    ):
                        # Convert timestamp to proper ISO format
                        dt = datetime.fromtimestamp(msg_date / 1000)
                        formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")

                        msg = {
                            "timestamp": formatted_date,
                            "type": (
                                "sent"
                                if elem.get("type") == "2"
                                else "received"
                            ),
                            "body": elem.get("body", ""),
                            "raw_timestamp": msg_date,  # Keep raw timestamp for sorting
                        }
                        messages.append(msg)
                elem.clear()

            # Sort by raw timestamp
            messages.sort(key=lambda x: x["raw_timestamp"])

            if output_format == "txt":
                with open(output_path, "w", encoding="utf-8") as f:
                    for msg in messages:
                        f.write(
                            f"[{msg['timestamp']}] {msg['type']}: {msg['body']}\n"
                        )
            else:  # CSV format
                import csv

                with open(output_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Type", "Message"])
                    for msg in messages:
                        writer.writerow(
                            [msg["timestamp"], msg["type"], msg["body"]]
                        )

            return output_path

        except Exception as e:
            st.error(f"Error exporting conversation: {str(e)}")
            raise e
