from pathlib import Path


def get_files(
    directory_path: str,
    allowed_extensions: set[str] | None = None,
    max_file_len: int = 24,
) -> tuple[list[Path], list[str]]:
    """Retrieve a list of files with specified extensions from a given directory"""
    allowed_extensions: set[str] = allowed_extensions or {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    directory: Path = Path(directory_path)

    files: list[Path] = []
    formatted_files: list[str] = []

    if not directory.exists() or not directory.is_dir():
        return [], []

    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in allowed_extensions:
            abbr_filename: str = f"{file.name[:max_file_len-4]}~{file.suffix}"
            formatted_file: str = abbr_filename if len(file.name) > max_file_len else file.name

            files.append(file)
            formatted_files.append(formatted_file)

    return files, formatted_files
