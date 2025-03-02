from pathlib import Path


def move_file(file_path: Path, target_dir: str) -> tuple[str, str]:
    """Moves a file to the target directory and returns a log message and its level"""
    file_name: str = file_path.name
    log_message: str = f"Move: {file_name} to {target_dir}\n"

    try:
        Path(target_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return (f"Creating dir \"{target_dir}\": {e}\n", "error")

    try:
        new_file_path: Path = Path(dir) / file_name
        file_path.rename(new_file_path)
        return (f"Moved new file path {new_file_path}: {log_message}", "success")
    except Exception as e:
        return (f"\"{log_message}\": {e}\n", "error")
