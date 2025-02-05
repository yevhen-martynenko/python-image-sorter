from pathlib import Path


def get_files(directory_path: str, allowed_extensions: set[str] = None) -> list[str]:
    """Retrieve a list of files with specified extensions from a given directory."""

    if allowed_extensions is None:
        allowed_extensions: set[str] = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

    directory: Path = Path(directory_path)
    files: list[str] = []

    if not directory.exists() or not directory.is_dir():
        return []

    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in allowed_extensions:
            formatted_file = f"{file.name[:12]}~{file.suffix}" if len(file.name) > 16 else file.name
            files.append(formatted_file)

    return files
