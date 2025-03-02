import curses
import subprocess
import shutil
from curses.textpad import rectangle
from pathlib import Path
from argparse import ArgumentParser, Namespace

from env import directory_path, target_directories
from image_sorter.ext import get_files, format_directories
from image_sorter.keybinding_actions import (
    move_file,
    copy_file,
    delete_file,
    rename_file,
    open_with_system_app,
)

from image_sorter.ext.parser import configure_parser
from image_sorter.ext.loggers import Logger
from image_sorter.gui.color import get_color, init_colors


# Define colors
BACKGROUND_COLOR = 1
TEXT_COLOR = 0
TEXT_HIGHLIGHT_COLOR = 100


class ImageSorter:
    SCROLL_OFFSET = 8

    def __init__(self, stdscr, directory_path, target_directories):
        self.stdscr = stdscr
        self.logger = Logger()
        self.directory_path = directory_path
        self.target_directories = target_directories
        self.load_files()
        self.scroll_pos = 0  # position of the first visible file
        self.selected_item_pos = 0 if self.num_files > 0 else -1

        self.setup_ui()

    def run(self):
        while True:
            self.stdscr.erase()
            self.draw_borders()

            self.display_file_list()  # TODO: parse situation with no images avaliable
            self.display_image()
            self.display_directories()
            self.stdscr.refresh()

            curses.flushinp()
            key = self.stdscr.getch()
            if key == -1:
                continue
            if self.handle_keypress(key):
                break

    def setup_ui(self):
        self.colors = init_colors()
        self.stdscr.keypad(True)  # enable keypad keys
        curses.curs_set(0)  # hide cursor
        curses.raw()
        # self.stdscr.nodelay(True)  # non-blocking input
        # self.stdscr.bkgd(" ", curses.color_pair(BACKGROUND_COLOR))

        self.height, self.width = self.stdscr.getmaxyx()
        self.max_visible = self.height - 4
        self.init_colunms()

    def init_colunms(self):
        col1_width = self.width // 4
        col2_width = self.width // 2
        col3_width = self.width - (col1_width + col2_width)

        self.cols = {
            "col1": (0, col1_width),
            "col2": (col1_width, col2_width),
            "col3": (col1_width+col2_width, col3_width)
        }
        self.bottom_y = self.height - 2 if self.height > 1 else self.height - 1

    def draw_borders(self):
        for col_name, (x, width) in self.cols.items():
            rectangle(self.stdscr, 0, x, self.bottom_y, x + width - 1)

    def load_files(self) -> None:
        """Loads files from the main directory"""
        self.raw_files, self.files = get_files(self.directory_path)
        self.num_files = len(self.files)

        if not self.files:
            self.logger.log_message(
                f"Failed to load files from {self.directory_path}",
                level="error"
            )
            self.selected_item_pos = -1

    def handle_keypress(self, key):
        if self.selected_item_pos >= 0:
            file_path: Path = self.raw_files[self.selected_item_pos]
        else:
            file_path = None

        self.logger.log_key_press(key)

        if key in (curses.KEY_DOWN, ord("j")):
            if self.selected_item_pos < self.num_files - 1:
                self.selected_item_pos += 1
            else:
                self.selected_item_pos = 0
                self.scroll_pos = 0

            is_scrollable: bool = (
                self.selected_item_pos >=
                self.scroll_pos + self.max_visible - self.SCROLL_OFFSET
            )
            if is_scrollable:
                self.scroll_pos += 1
            if self.scroll_pos > self.num_files - self.max_visible:
                self.scroll_pos = max(0, self.num_files - self.max_visible)

        elif key in (curses.KEY_UP, ord("k")):
            if self.selected_item_pos > 0:
                self.selected_item_pos -= 1
            else:
                self.selected_item_pos = self.num_files - 1
                self.scroll_pos = self.num_files - self.max_visible

            is_scrollable: bool = (
                self.selected_item_pos <
                self.scroll_pos + self.SCROLL_OFFSET
            )
            if is_scrollable:
                self.scroll_pos -= 1
            if self.scroll_pos < 0:
                self.scroll_pos = 0

        elif key in (curses.KEY_DC, ord("d")):
            safe_delete = True  # TODO: get with argparse
            delete_file(file_path, safe_delete)  # TODO: delete file

        elif key in (curses.KEY_F2, ord("r")):
            # rename_file(file_path, new_name)  # TODO: rename file, make a prompt for new_name
            ...

        elif key in (curses.KEY_F1, ord("h")):
            ...  # TODO: open help menu

        elif key in (curses.KEY_ENTER, 10, 13):
            open_with_system_app(file_path)  # TODO: open image in new window in default image viewer

        elif key in (ord("q"), 27):  # 27 - ESC
            return True

        elif file_path:
            self.process_keypress(key, file_path)

        return False

    def process_keypress(self, key: int, file_path: Path, is_copy: bool = False) -> None:  # TODO: get is_copy with argparse
        """Handles keypress events for moving or copying files to target directories"""
        target_index: int = key - ord('0')

        if 1 <= target_index <= len(self.target_directories):
            target_dir = self.target_directories[target_index - 1]

            if is_copy:
                copy_file(file_path, target_dir)
            else:
                log_message, log_level = move_file(file_path, target_dir)
                self.logger.main_log(log_message, log_level)
                self.load_files()

    def display_file_list(self) -> None:
        """Display a list of files in the first column with scrolling functionality."""
        for i in range(min(self.max_visible, len(self.files) - self.scroll_pos)):
            file_index: int = self.scroll_pos + i
            if file_index >= self.num_files:
                break

            formatted_line: str = f"{file_index:>{len(str(self.num_files))}}  {self.files[file_index]}"
            formatted_line = formatted_line.ljust(self.cols["col1"][0] - 4)

            # TODO: use get_color instead curses.color_pair
            attr = curses.color_pair(TEXT_HIGHLIGHT_COLOR) if file_index == self.selected_item_pos else curses.color_pair(TEXT_COLOR)
            self.stdscr.addstr(1 + i, self.cols['col1'][0] + 2, formatted_line, attr)

    def display_image(self) -> None:
        """Displays an image using Kitty's icat with a dynamically sized picture"""
        if self.selected_item_pos < 0:
            return

        file_path: Path = self.raw_files[self.selected_item_pos]
        col2_x: int = self.cols["col2"][0]

        term_width, term_height = shutil.get_terminal_size()
        img_width: int = max(10, term_width - 2 * col2_x - 5)
        img_height: int = max(10, term_height - 4)
        img_pos_left: int = col2_x + 1  # col2_x + border width
        img_pos_top: int = 1  # border width

        # subprocess.run(["clear"])
        self.stdscr.refresh()

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
            self.stdscr.addstr(1, col2_x + 2, error_message, curses.color_pair(TEXT_COLOR))

    def display_directories(self) -> None:
        formatted_dirs: list[str] = format_directories(self.target_directories, num_levels=2)

        for i, dir in enumerate(formatted_dirs, start=1):
            formatted_line: str = f"{i:>{len(str(i))}}  {dir}"
            self.stdscr.addstr(
                i, self.cols["col3"][0] + 2,
                formatted_line,
                curses.color_pair(TEXT_COLOR)  # TODO: change to get_color()
            )


def main(stdscr):
    app: ImageSorter = ImageSorter(stdscr, directory_path, target_directories)
    parser: ArgumentParser = configure_parser()
    args: Namespace = parser.parse_args()

    if args.help:
        parser.print_help()
    else:
        app.run()


if __name__ == "__main__":
    curses.wrapper(main)
