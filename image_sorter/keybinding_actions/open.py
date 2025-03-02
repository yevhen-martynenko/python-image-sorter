import subprocess
import sys
from pathlib import Path


def open_with_system_app(file_path: Path) -> None:
    """Open an image with the default application"""
    if sys.platform == "linux" or sys.platform == "linux2":
        subprocess.run(["xdg-open", file_path])
    elif sys.platform == "darwin":
        subprocess.run(["open", file_path])  # For macOS
    else:
        print(f"Unsupported OS: {sys.platform}")
