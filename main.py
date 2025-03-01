import curses
import subprocess
import shutil
import logging
from curses.textpad import rectangle
from pathlib import Path
from argparse import ArgumentParser, Namespace

from image_sorter.ext.get_files import get_files
from image_sorter.ext.format_dirs import format_directories
from image_sorter.ext.parser import configure_parser
from image_sorter.functions_triggered_by_keyblindings.move import move_file
from image_sorter.gui.color import get_color, init_colors

from env import directory_path, target_directories


# Define colors
BACKGROUND_COLOR = 1
TEXT_COLOR = 0
TEXT_HIGHLIGHT_COLOR = 100


class ImageSorter:
    SCROLL_OFFSET = 8

    def __init__(self, stdscr, directory_path, target_directories):
        self.stdscr = stdscr
        self.directory_path = directory_path
        self.target_directories = target_directories
        self.raw_files, self.files = get_files(self.directory_path)
        self.num_files = len(self.files)
        self.scroll_pos = 0  # position of the first visible file
        self.selected_item_pos = 0 if self.num_files > 0 else -1
        self.prev_key = None

        self.setup_ui()

    def run(self):
        while True:
            self.stdscr.erase()
            self.draw_borders()

            self.display_file_list()
            self.display_image()
            self.display_directories()
            self.stdscr.refresh()

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

    def handle_keypress(self, key):
        file_path: Path = self.raw_files[self.selected_item_pos] if self.selected_item_pos >= 0 else None
        key_logger(key, self.prev_key)

        self.prev_key = key if key != 27 else self.prev_key

        # TODO: make functionality of going to the first/last element after reaching top/bottom + 1
        # BUG: while holding j or k unexpected behavior - processing random keys (key_down and key_up work fine)
        # BUG: maybe because curses process holding keys as some sequence of different keys 
        if key in (curses.KEY_DOWN, ord("j")) and self.selected_item_pos < self.num_files - 1:
            self.selected_item_pos += 1
            
            #is_scrollable: bool = self.selected_item_pos >= self.scroll_pos + self.max_visible - self.SCROLL_OFFSET
            is_scrollable: bool = self.selected_item_pos >= self.scroll_pos + self.height - 4 - self.SCROLL_OFFSET
            if is_scrollable:
                self.scroll_pos += 1
            if self.scroll_pos > self.num_files - self.max_visible:
                self.scroll_pos = max(0, self.num_files - self.max_visible)
            
        elif key in (curses.KEY_UP, ord("k")) and self.selected_item_pos > 0:
            self.selected_item_pos -= 1
            
            is_scrollable: bool = self.selected_item_pos < self.scroll_pos + self.SCROLL_OFFSET
            if is_scrollable:
                self.scroll_pos -= 1
            if self.scroll_pos < 0:
                self.scroll_pos = 0

        elif key in (curses.KEY_DC, ord("d")):
            ...  # TODO: delete file

        elif key in (curses.KEY_F2, ord("r")):
            ...  # TODO: rename file

        elif key in (curses.KEY_F1, ord("h")):
            ...  # TODO: open help menu

        #elif key == Enter:
            ...  # TODO: open image in new window in default image viewer

        elif key == ord("q"):  # TODO: add ESC (27) key
            return True  # TODO: close the program

        elif file_path:
            self.process_keypress(key, file_path)

        return False

    def process_keypress(self, key, file_path: Path) -> None:
        for i, target_dir in enumerate(self.target_directories, start=1):
            if key == ord(str(i)):
                self.move_file(file_path, target_dir)

                if 0 <= self.selected_item_pos < len(self.files):  # Prevent IndexError
                    del self.files[self.selected_item_pos]
                else:  # TODO: remove logging
                    logging.warning(f"Invalid index: {self.selected_item_pos} (out of range)")

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
        """Displays an image using Kitty's icat without ruining the terminal borders."""
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


def key_logger(key: int, prev_key: int) -> None:
    with open("logs/keys.log", "a") as f:
        if key == curses.KEY_DOWN:
            f.write(f"KEY_DOWN is pressed: {key}. Previous key: {prev_key}\n")
        elif key == curses.KEY_UP:
            f.write(f"KEY_UP is pressed: {key}. Previous key: {prev_key}\n")
        else:
            f.write(f"Key: {key}. Previous key: {prev_key}\n")


def logging_change_name(message: str, *args) -> None:
    with open("logs/custom.log", "a") as f:
        f.write(f"{message}: {', '.join(map(str, args))}\n")


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
