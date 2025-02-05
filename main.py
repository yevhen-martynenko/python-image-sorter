from __future__ import absolute_import

import curses
from curses.textpad import rectangle

from image_sorter.ext.get_files import get_files

# Define colors
BACKGROUND_COLOR = 1
TEXT_COLOR = 8


def init_color():
    """Initialize terminal color palette"""
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)


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

    directory_path = "/home/user/Download"  # TODO: use argparse
    files_in_directory = get_files(directory_path)
    num_files = len(files_in_directory)

    scroll_pos = 0
    max_visible = height - 4

    while True:
        stdscr.erase()
        stdscr.refresh()

        # Redraw borders
        rectangle(stdscr, 0, col1_x, bottom_y, col1_x + col1_width - 1)
        rectangle(stdscr, 0, col2_x, bottom_y, col2_x + col2_width - 1)
        rectangle(stdscr, 0, col3_x, bottom_y, col3_x + col3_width - 1)

        # Display content
        display_file_list(stdscr, files_in_directory, scroll_pos, col1_x)
        display_image(stdscr, col2_x)
        display_directories(stdscr, col3_x)

        stdscr.refresh()

        # parse_keybinding(stdscr)
        key = stdscr.getch()
        if key == curses.KEY_DOWN and scroll_pos + max_visible < num_files:
            scroll_pos += 1
        elif key == curses.KEY_UP and scroll_pos > 0:
            scroll_pos -= 1
        elif key == ord("q"):
            break


def display_file_list(
    stdscr, files_dir: list[str], scroll_pos: int, col1_x: int
) -> None:
    """Display a list of files in the first column with scrolling functionality."""
    max_visible = stdscr.getmaxyx()[0] - 4
    num_files: int = len(files_dir)

    for i in range(max_visible):
        file_index: int = scroll_pos + i

        if file_index >= num_files:
            break

        formatted_line: str = (
            f"{file_index:>{len(str(num_files))}}  {files_dir[file_index]}"
        )
        stdscr.addstr(1 + i, col1_x + 2, formatted_line, curses.color_pair(TEXT_COLOR))


def display_image(stdscr, col2_x: int) -> None:
    stdscr.addstr(1, col2_x + 2, "Column 2: image", curses.color_pair(TEXT_COLOR))


def display_directories(stdscr, col3_x: int) -> None:
    stdscr.addstr(1, col3_x + 2, "Column 3: dirs", curses.color_pair(TEXT_COLOR))


curses.wrapper(main)
