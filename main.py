from __future__ import absolute_import

import subprocess
import shutil
import os
import curses
from curses.textpad import rectangle
from pathlib import Path

from image_sorter.ext.get_files import get_files
from image_sorter.ext.format_dirs import format_directories
from image_sorter.ext.parser import configure_parser

from image_sorter.gui.color import get_color, init_colors
from env import directory_path, target_directories 


# Define colors
BACKGROUND_COLOR = 1
TEXT_COLOR = 0
TEXT_HIGHLIGHT_COLOR = 100


def main(stdscr):
    curses.curs_set(0)  # hide cursor
    colors = init_colors()
    # stdscr.bkgd(" ", curses.color_pair(BACKGROUND_COLOR))
    stdscr.erase()
    stdscr.keypad(True)  # enable keypad keys
    curses.raw()
    # stdscr.nodelay(True)  # non-blocking input


    height, width = stdscr.getmaxyx()

    col1_width = width // 4
    col2_width = width // 2
    col3_width = width - (col1_width + col2_width)

    col1_x = 0
    col2_x = col1_width
    col3_x = col1_width + col2_width

    bottom_y = height - 2 if height > 1 else height - 1

    stdscr.erase()
    for x in [col1_x, col2_x, col3_x]:
        rectangle(stdscr, 0, x, bottom_y, x + col1_width - 1)

    raw_files_in_directory, files_in_directory = get_files(directory_path)
    num_files = len(files_in_directory)

    scroll_pos = 0  # position of the first visible file
    selected_item_pos = 0 if num_files > 0 else -1 
    max_visible = height - 4
    SCROLL_OFFSET = 8
    prev_key = None

    while True:
        stdscr.erase()

        # Redraw borders
        rectangle(stdscr, 0, col1_x, bottom_y, col1_x + col1_width - 1)
        rectangle(stdscr, 0, col2_x, bottom_y, col2_x + col2_width - 1)
        rectangle(stdscr, 0, col3_x, bottom_y, col3_x + col3_width - 1)

        # Display content
        display_file_list(stdscr, files_in_directory, scroll_pos, selected_item_pos, col1_width, col1_x)
        display_image(stdscr, directory_path, raw_files_in_directory, scroll_pos, selected_item_pos, col2_x)
        display_directories(stdscr, target_directories, col3_x)

        stdscr.refresh()

        # parse_keybinding(stdscr)
        key = stdscr.getch()

        if key == -1:
            continue
        
        # file_path = get_current_file_path(directory_path, files_in_directory, selected_item_pos)
        file_path: Path = raw_files_in_directory[selected_item_pos]
        
        with open("keys.log", "a") as f:
            f.write(f"Key: {key}\n")
        
        if key == 27 and prev_key is not None:
            key = prev_key  
        prev_key = key if key != 27 else prev_key

        # TODO: make functionality of going to the first/last element after reaching top/bottom + 1
        if key in (curses.KEY_DOWN, ord("j")) and selected_item_pos < num_files - 1:
            selected_item_pos += 1

            is_scrollable: bool = selected_item_pos >= scroll_pos + max_visible - SCROLL_OFFSET
            if is_scrollable:
                scroll_pos += 1
            if scroll_pos > num_files - max_visible:
                scroll_pos = max(0, num_files - max_visible)

        elif key in (curses.KEY_UP, ord("k")) and selected_item_pos > 0:
            selected_item_pos -= 1

            is_scrollable: bool = selected_item_pos < scroll_pos + SCROLL_OFFSET
            if is_scrollable:
                scroll_pos -= 1
            if scroll_pos < 0:
                scroll_pos = 0

        elif key in (curses.KEY_DC, ord("d")):
            # TODO: delete file
            ...

        elif key in (curses.KEY_F2, ord("r")):
            # TODO: rename file without moving it 
            ...

        elif key in (curses.KEY_F1, ord("h")):
            # TODO: open help menu
            ...

        elif key == ord("q"):  # 27 - ESC key
            break

        for i, dir in enumerate(target_directories, start=1):
            if key == ord(str(i)):
                move_file(file_path, dir)


def move_file(file_path: Path, dir: str) -> None:
    file_name: str = file_path.name
    log_message: str = f"Move: {file_name} to {dir}\n"

    try:
        Path(dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        log_message = f"__ERROR__ while creating dir \"{dir}\": {e}\n"

    try:
        new_file_path: Path = Path(dir) / file_name
        file_path.rename(new_file_path)
        log_message = f"__MOVED__ new file path {new_file_path}: {log_message}"
    except Exception as e:
        log_message = f"__ERROR__ \"{log_message}\": {e}\n"

    with open("main.log", "a") as f:
        f.write(log_message)


def display_file_list(
    stdscr,
    files_dir: list[str],
    scroll_pos: int, selected_item_pos: int,
    col1_width: int, col1_x: int
) -> None:
    """Display a list of files in the first column with scrolling functionality."""
    max_visible = stdscr.getmaxyx()[0] - 4
    num_files: int = len(files_dir)

    for i in range(max_visible):
        file_index: int = scroll_pos + i

        if file_index >= num_files:
            break

        formatted_line: str = f"{file_index:>{len(str(num_files))}}  {files_dir[file_index]}"
        formatted_line = formatted_line.ljust(col1_width - 4)

        if file_index == selected_item_pos:
            stdscr.addstr(1 + i, col1_x + 2, formatted_line, curses.color_pair(TEXT_HIGHLIGHT_COLOR))
        else:
            stdscr.addstr(1 + i, col1_x + 2, formatted_line, curses.color_pair(TEXT_COLOR))


def display_image(
    stdscr,
    directory_path: str, files_dir: list[str],
    scroll_pos: int, selected_item_pos: int,
    col2_x: int
) -> None:
    """Displays an image using Kitty's icat without ruining the terminal borders."""
    # file_path = get_current_file_path(directory_path, files_dir, selected_item_pos)
    file_path: Path = files_dir[selected_item_pos]

    term_width, term_height = shutil.get_terminal_size()
    img_width: int = max(10, term_width - 2 * col2_x - 5)
    img_height: int = max(10, term_height - 4)
    img_pos_left: int = col2_x + 1  # col2_x + border width
    img_pos_top: int = 1  # border width

    # subprocess.run(["clear"])
    stdscr.refresh()

    try:
        subprocess.run([
            "kitty", "icat",
            "--align", "left",
            "--place", f"{img_width}x{img_height}@{img_pos_left}x{img_pos_top}",
            "--no-trailing-newline", "--silent",
            "--clear",
            str(file_path)
        ], stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError as e:
        error_message: str = f"Error displaying image: {e}"
        stdscr.addstr(1, col2_x + 2, error_message, curses.color_pair(TEXT_COLOR))


def display_directories(
    stdscr,
    target_dirs: list[str],
    col3_x: int
) -> None:
    formatted_dirs: list[str] = format_directories(target_dirs)

    for i, dir in enumerate(formatted_dirs, start=1):
        formatted_line: str = f"{i:>{len(str(i))}}  {dir}"
        stdscr.addstr(
            i, col3_x + 2,
            formatted_line, curses.color_pair(TEXT_COLOR)
        )


if __name__ == "__main__":
    parser = configure_parser()
    args = parser.parse_args()

    if args.help:
        parser.print_help()
    elif args.version:
        # print_version()
        pass
    else:
        curses.wrapper(main)
