import shutil
from pathlib import Path


def move_file(
    file_path: Path,
    target_dir: str,
    auto_rename: int,
    copy_mode: bool
) -> tuple[str, str]:
    """Moves or copies a file to the target directory and returns a log message and its level"""
    file_name: str = file_path.name
    target_dir_path: Path = create_target_dir(target_dir)

    if auto_rename:
        max_file_name: str = get_next_available_filename(target_dir_path)
        new_name: Path = target_dir_path / max_file_name
    else:
        new_name: Path = target_dir_path / file_name

    try:
        if copy_mode:
            shutil.copy2(file_path, new_name)
            return (f'File "{file_name}" successfully copied to {new_name}', "success")
        else:
            shutil.move(str(file_path), str(new_name))
            return (f'File "{file_name}" successfully moved to {new_name}', "success")
    except Exception as e:
        action: str = "Copying" if copy_mode else "Moving"
        return (f'{action} file "{file_name}" to {target_dir}: {e}', "error")


def create_target_dir(target_dir: str) -> Path:
    """Creates a target directory if it does not exist"""
    target_dir_path: Path = Path(target_dir)

    try:
        target_dir_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return (f'Creating target directory "{target_dir}": {e}', "error")

    return target_dir_path


def get_next_available_filename(target_dir: Path) -> str:
    """Finds the next avaliable numbered filename in the target directory"""
    existing_numbers: list[int] = []
    file_suffix: str = ".jpg"

    for file in target_dir.iterdir():
        if file.is_file() and file.stem.isdigit():
            existing_numbers.append(int(file.stem))
            file_suffix = file.suffix

    existing_numbers.sort()

    next_number: int = 1
    for num in existing_numbers:
        if num == next_number:
            next_number += 1
        else:
            break

    return f"{next_number}{file_suffix}"
