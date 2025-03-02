from pathlib import Path


def delete_file(file_path: Path, safe: bool = True) -> tuple[str, str]:
    file_name: str = file_path.name

    if safe:
        try:
            trash_dir: Path = Path("~/.trash/image_sorter/").expanduser()
            Path(trash_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return (f"Creating trash directory \"{trash_dir}\": {e}", "error")

        try:
            new_file_path: Path = Path(trash_dir) / file_name
            file_path.rename(new_file_path)
            return (f"File \"{file_name}\" successfully moved to \"{trash_dir}\"", "success")
        except Exception as e:
            return (f"Moving file \"{file_name}\" to trash: {e}", "error")
    else:
        try:
            file_path.unlink()
            return (f"File \"{file_name}\" permanently deleted from {file_path}", "success")
        except Exception as e:
            return (f"Permanently deleting file \"{file_name}\": {e}", "error")
