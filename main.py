from __future__ import absolute_import

import subprocess
import shutil
import curses
from curses.textpad import rectangle
from pathlib import Path

from image_sorter.ext.get_files import get_files
from image_sorter.ext.format_dirs import format_directories
from image_sorter.ext.parser import configure_parser


# Define colors
BACKGROUND_COLOR = 1
TEXT_COLOR = 8
TEXT_HIGHLIGHT_COLOR = 100


def init_color():
    """Initialize terminal color palette"""
    curses.start_color()
    curses.use_default_colors()

    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    # user defined colors
    curses.init_pair(TEXT_HIGHLIGHT_COLOR, 232, 231)


def main(stdscr):
    curses.curs_set(0)
    init_color()
    # stdscr.bkgd(" ", curses.color_pair(BACKGROUND_COLOR))
    stdscr.erase()

    height, width = stdscr.getmaxyx()

    col1_width = width // 4
    col2_width = width // 2
    col3_width = width - (col1_width + col2_width)

    col1_x = 0
    col2_x = col1_width
    col3_x = col1_width + col2_width

    bottom_y = height - 2 if height > 1 else height - 1

    rectangle(stdscr, 0, col1_x, bottom_y, col1_x + col1_width - 1)
    rectangle(stdscr, 0, col2_x, bottom_y, col2_x + col2_width - 1)
    rectangle(stdscr, 0, col3_x, bottom_y, col3_x + col3_width - 1)

    directory_path = "/home/spes/Downloads/arts/2"  # TODO: use argparse
    target_directories = [
        "/home/user/Downloads/images/1/",
        "/home/user/Downloads/images/2/",
        "/home/user/Downloads/images/3/",
        "/home/user/Downloads/images/4/",
        "/home/user/Downloads/images/5/",
    ]
    raw_files_in_directory, files_in_directory = get_files(directory_path)
    num_files = len(files_in_directory)

    scroll_pos = 0  # position of the first visible file
    selected_item_pos = 0
    max_visible = height - 4

    while True:
        stdscr.erase()
        stdscr.refresh()

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

        SCROLL_OFFSET = 8
        # file_path = get_current_file_path(directory_path, files_in_directory, selected_item_pos)
        file_path: Path = raw_files_in_directory[selected_item_pos]

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

        elif key in (curses.DELETE, ord("d")):
            # TODO: delete file
            ...

        elif key in (ord("F2"), ord("r")):
            # TODO: rename file without moving it 
            ...

        elif key in (ord("F1"), ord("h")):
            # TODO: open help menu
            ...

        elif key in (ord("Esc"), ord("q")):
            break


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

    for i, dir in enumerate(formatted_dirs):
        formatted_line: str = f"{i:>{len(str(i))}}  {dir}"
        stdscr.addstr(
            i + 1, col3_x + 2,
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
