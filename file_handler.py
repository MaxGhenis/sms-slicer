from pathlib import Path
import platform
import subprocess


def get_default_download_dir():
    """Get the default downloads directory for the current OS"""
    system = platform.system()
    if system == "Darwin":  # macOS
        return str(Path.home() / "Downloads")
    elif system == "Windows":
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
        ) as key:
            return winreg.QueryValueEx(
                key, "{374DE290-123F-4565-9164-39C4925E467B}"
            )[0]
    else:  # Linux and others
        return str(Path.home() / "Downloads")


def find_sms_backups(directory=None):
    """Find SMS backup files in the given directory"""
    if directory is None:
        directory = get_default_download_dir()

    path = Path(directory)
    if not path.exists():
        return []

    # Look for SMS backup files (common patterns)
    backup_files = []
    patterns = ["sms-*.xml", "SMS*.xml", "*backup*.xml"]
    for pattern in patterns:
        backup_files.extend(path.glob(pattern))

    # Sort by modification time, newest first
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return backup_files


def open_file_location(path):
    """Open the file location in the system file explorer"""
    system = platform.system()
    path = Path(path)

    if system == "Darwin":  # macOS
        subprocess.run(["open", "-R", str(path)])
    elif system == "Windows":
        subprocess.run(["explorer", "/select,", str(path)])
    else:  # Linux
        subprocess.run(["xdg-open", str(path.parent)])


def validate_file(file_path):
    """Validate the selected file path"""
    if not file_path:
        return False, "No file selected"

    path = Path(file_path)
    if not path.exists():
        return False, f"File not found: {file_path}"
    if path.suffix.lower() != ".xml":
        return False, "Selected file is not an XML file"

    return True, path
