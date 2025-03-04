import curses
import subprocess
import shutil
from curses.textpad import rectangle, Textbox
from pathlib import Path
from argparse import ArgumentParser, Namespace

from image_sorter.ext.parser import configure_parser
from image_sorter.ext.loggers import Logger
from image_sorter.gui.ui import UI
from image_sorter.ext import (
    get_files,
    format_directories,
    validate_args,
)
from image_sorter.keybinding_actions import (
    move_file,
    delete_file,
    rename_file,
    open_with_system_app,
)


class ImageSorter:
    SCROLL_OFFSET = 8

    def __init__(self, stdscr, args):
        self.stdscr = stdscr
        self.args = args
        self.logger = Logger()
        self.ui = UI(self.args.theme)
        self.directory_path: str = args.input_dir
        self.target_directories: list[str] = args.output_dirs
        self.files_avaliable = True
        self.load_files()
        self.scroll_pos = 0  # position of the first visible file
        self.selected_item_pos = 0 if self.num_files > 0 else -1

        self.setup_ui()

    def run(self):
        while True:
            self.stdscr.erase()
            self.draw_borders()

            if self.files_avaliable:
                self.display_file_list()
                self.display_image()
                self.display_directories()
            else:
                self.stdscr.addstr(
                    1, self.cols['col1'][0] + 2,
                    "No files available",
                    self.ui.get_color("error")
                )

            self.stdscr.refresh()

            curses.flushinp()
            key = self.stdscr.getch()
            if key == -1:
                continue
            if self.handle_keypress(key):
                break

    def setup_ui(self):
        self.colors = self.ui.load_colors()
        self.logger.log_custom_event("self.colors: ", self.colors)
        self.stdscr.keypad(True)  # enable keypad keys
        curses.curs_set(0)        # hide cursor
        curses.raw()

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
        # TODO: apply colors to borders from the color scheme
        for col_name, (x, width) in self.cols.items():
            rectangle(self.stdscr, 0, x, self.bottom_y, x + width - 1)

    def load_files(self) -> None:
        """Loads files from the main directory"""
        if self.args.tree:
            directories: list[Path] = [d for d in Path(self.directory_path).iterdir() if d.is_dir()]
            directories.append(Path(self.directory_path))

            raw_files, files = [], []
            for dir in directories:
                raw_f, f = get_files(dir)
                raw_files.extend(raw_f)
                files.extend(f)

            self.raw_files, self.files = raw_files, files
        else:
            self.raw_files, self.files = get_files(self.directory_path)

        self.num_files = len(self.files)

        if not self.files:
            self.logger.log_message(
                f"Failed to load files from {self.directory_path}",
                level="error"
            )
            self.selected_item_pos = -1
            self.files_avaliable = False

    def handle_keypress(self, key):
        if not self.files_avaliable:
            return True

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
            log_message, log_level = delete_file(
                file_path,
                self.args.safe_delete
            )
            self.logger.log_message(log_message, log_level)
            self.load_files()

        elif key in (curses.KEY_F2, ord("r")):
            # rename_file(file_path, new_name)  # TODO: rename file, make a prompt for new_name. use curses Textbox
            ...

        elif key in (curses.KEY_F1, ord("h")):
            ...  # TODO: open help menu

        elif key in (curses.KEY_ENTER, 10, 13):
            open_with_system_app(file_path)

        elif key in (ord("q"), 27):  # 27 - ESC
            return True

        elif file_path:
            self.process_keypress(key, file_path)

        return False

    def process_keypress(self, key: int, file_path: Path) -> None:
        """Handles keypress events for moving or copying files to target directories"""
        target_index: int = key - ord('0')

        if 1 <= target_index <= len(self.target_directories):
            target_dir = self.target_directories[target_index - 1]

            log_message, log_level = move_file(
                file_path,
                target_dir,
                self.args.auto_rename,
                self.args.copy_mode
            )

            self.logger.log_message(log_message, log_level)
            self.load_files()

    def display_file_list(self) -> None:
        """Display a list of files in the first column with scrolling functionality"""
        for i in range(min(self.max_visible, len(self.files) - self.scroll_pos)):
            file_index: int = self.scroll_pos + i
            if file_index >= self.num_files:
                break

            file_index_length: int = len(str(self.num_files))
            file_index_str: str = f"{file_index:>{file_index_length}}"
            max_line_length: int = max(len(f) for f in self.files)
            file_name: str = self.files[file_index]

            formatted_line: str = f"{file_index_str}  {file_name:<{max_line_length}}"
            formatted_line = formatted_line.ljust(self.cols["col1"][0] - 4)

            if file_index == self.selected_item_pos:
                attr = self.ui.get_color("text_highlight", self.ui.elements.get("cursor", "normal"))
            else:
                attr = self.ui.get_color("text")
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

        mirror = "none"
        mirror_horizontal = self.ui.elements.get("mirror", False)
        mirror_vertical = self.ui.elements.get("mirror_vertical", False)

        if mirror_horizontal and mirror_vertical:
            mirror = "both"
        elif mirror_horizontal:
            mirror = "horizontal"
        elif mirror_vertical:
            mirror = "vertical"

        try:
            subprocess.run([
                "kitty", "icat",
                "--align", "left",
                "--place", f"{img_width}x{img_height}@{img_pos_left}x{img_pos_top}",
                "--no-trailing-newline", "--silent",
                "--mirror", mirror,
                "--clear",
                str(file_path)
            ], stderr=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError as e:
            error_message: str = "Error displaying image"  # : {e}"
            self.stdscr.addstr(1, col2_x + 2, error_message, self.ui.get_color("error"))

    def display_directories(self) -> None:
        """Displays formatted target directories with indexed previews"""
        MAX_DISPLAY = 30
        PREFIX_MAP = {10: "c+", 20: "a+"}  # TODO: add keypress events for this, c+ CTRL+KEY, a+ ALT+KEY

        formatted_dirs: list[str] = format_directories(
            self.target_directories,
            num_levels=2
        )
        max_display_limit: int = min(MAX_DISPLAY, len(formatted_dirs))
        max_index_length: int = len(str(max_display_limit))

        if len(formatted_dirs) >= 10:
            max_index_length += 1

        for i, dir in enumerate(formatted_dirs[:MAX_DISPLAY], start=1):
            prefix: str = next((v for k, v in PREFIX_MAP.items() if i >= k), "")
            preview: str = f"{prefix}{i % 10}" if prefix else str(i)
            formatted_line: str = f"{preview:<{max_index_length}}  {dir}"

            self.stdscr.addstr(
                i, self.cols["col3"][0] + 2,
                formatted_line,
                self.ui.get_color("text")
            )


def main(stdscr, args):
    app: ImageSorter = ImageSorter(stdscr, args)
    app.run()


if __name__ == "__main__":
    parser: ArgumentParser = configure_parser()
    args: Namespace = parser.parse_args()

    validate_args(args)

    if args.help:
        parser.print_help()
    else:
        curses.wrapper(main, args)
