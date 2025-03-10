import curses

from image_sorter.gui.color import init_colors
from image_sorter.gui.colorscheme import ColorScheme


class UI:
    def __init__(self, theme="default"):
        self.theme = theme
        self.colorscheme = ColorScheme(self.theme)
        self.text_styles = {
            "normal": curses.A_NORMAL,
            "bold": curses.A_BOLD,
            "blink": curses.A_BLINK,
            "reverse": curses.A_REVERSE,
            "underline": curses.A_UNDERLINE,
            "invisible": curses.A_INVIS,
            "dim": curses.A_DIM,
        }
        self.colors = {}
        self.elements = {}

    def load_colors(self) -> dict[str, tuple[int, int]]:
        self.colors = self.colorscheme.get_colors()
        self.elements = self.colorscheme.get_elements()

        init_colors(default_colors={}, colors=self.colors)
        return self.colors

    def get_color(self, color: int | str = 1, style: str = "normal") -> int:
        """Retrieve a color pair for use in curses"""
        if isinstance(color, int):
            color_pair = curses.color_pair(color)
        elif isinstance(color, str):
            color_index = self.colors.get(color.lower(), 1)
            color_pair = curses.color_pair(color_index[0])

        style_flag = self.text_styles.get(style, curses.A_NORMAL)
        return color_pair | style_flag
