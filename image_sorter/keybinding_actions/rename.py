from pathlib import Path


def rename_file(file_path: Path, new_name: str) -> tuple[str, str]:
    """Renames a file to a new name within the same directory"""
    if not file_path.exists():
        return (f'File "{file_path}" not found.', "error")

    dir_path: Path = file_path.parent
    new_path: Path = dir_path / new_name

    try:
        file_path.rename(new_path)
        return (f'File "{file_path.name}" successfully renamed to "{new_name}"', "success")
    except Exception as e:
        return (f'Renaming file "{file_path.name}" to {new_name}: {e}', "error")
