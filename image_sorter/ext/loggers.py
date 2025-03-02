import curses
from pathlib import Path


class Logger:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.main_log = self.log_dir / "main.log"
        self.keys_log = self.log_dir / "keys.log"
        self.custom_log = self.log_dir / "custom.log"

    def log_message(self, message: str, level: str = "info") -> None:
        """Logs a message with a specified log level (INFO, ERROR, etc)"""
        with open(self.main_log, "a") as f:
            f.write(f"__{level.upper()}__: {message}\n")

    def log_key_press(self, key: int) -> None:
        """Logs key press events"""
        with open(self.keys_log, "a") as f:
            if key == curses.KEY_DOWN:
                f.write(f"KEY_DOWN is pressed: {key}\n")
            elif key == curses.KEY_UP:
                f.write(f"KEY_UP is pressed: {key}\n")
            else:
                f.write(f"Key pressed: {key}\n")

    def log_custom_event(self, event: str, *args) -> None:
        """Logs custom events with additional variables"""
        with open(self.custom_log, "a") as f:
            f.write(f"{event}: {', '.join(map(str, args))}\n")
