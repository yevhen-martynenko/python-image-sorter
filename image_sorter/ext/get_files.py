from pathlib import Path


def get_files(
        directory_path: str,
        allowed_extensions: set[str] | None = None
) -> tuple[list[Path], list[str]]:
    """Retrieve a list of files with specified extensions from a given directory."""

    allowed_extensions: set[str] = allowed_extensions or {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    directory: Path = Path(directory_path)

    files: list[Path] = []
    formatted_files: list[str] = []

    if not directory.exists() or not directory.is_dir():
        return [], []

    for file in directory.iterdir():
        files.append(file)

        if file.is_file() and file.suffix.lower() in allowed_extensions:
            formatted_file = f"{file.name[:12]}~{file.suffix}" if len(file.name) > 16 else file.name
            formatted_files.append(formatted_file)

    return files, formatted_files
