from pathlib import Path


def move_file(file_path: Path, dir: str) -> None:
    file_name: str = file_path.name
    log_message: str = f"Move: {file_name} to {dir}\n"

    try:
        Path(dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        log_message = f"__ERROR__ while creating dir \"{dir}\": {e}\n"
        return

    try:
        new_file_path: Path = Path(dir) / file_name
        file_path.rename(new_file_path)
        log_message = f"__MOVED__ new file path {new_file_path}: {log_message}"
    except Exception as e:
        log_message = f"__ERROR__ \"{log_message}\": {e}\n"

    with open("logs/main.log", "a") as f:
        f.write(log_message)
