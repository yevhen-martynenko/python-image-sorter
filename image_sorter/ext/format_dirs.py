def format_directories(dirs: list[str], num_levels: int = 3) -> list[str]:
    """Format directories"""
    formatted_dirs: list[str] = []

    for dir in dirs:
        path_parts: str = dir.split("/")

        if len(path_parts) > num_levels:
            abbr_path: str = "/".join([i[:1] for i in path_parts[:-num_levels]] + path_parts[-num_levels:])
        else:
            abbr_path: str = dir

        formatted_dirs.append(abbr_path)

    return formatted_dirs
