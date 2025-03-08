import json
from pathlib import Path


class ColorScheme:
    """Base class for defining color schemes"""

    def __init__(self, name: str):
        self.name = name
        self.json_file = Path(__file__).parent / "colorschemes.json"
        self.default_colors = {
            "foreground": 15,
            "background": 0,
        }
        self.colors = {
            "text": [15, -1],
            "text_highlight": [15, -1],
            "error": [9, -1]
        }
        self.elements = {
            "cursor": "reverse",
            "mirror": False,
            "mirror_vertical": False
        }
        self.load_colorscheme()

    def get_colors(self) -> dict[str, tuple[int, int]]:
        return self.colors

    def get_elements(self) -> dict[str, str]:
        return self.elements

    def load_colorscheme(self):
        """Load colors and elements from the JSON file"""
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)

            if self.name in data:
                scheme = data[self.name]
                self.default_colors = scheme.get("default_colors", self.default_colors)
                self.colors = scheme.get("colors", self.colors)
                self.elements = scheme.get("elements", self.elements)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # use default colorscheme

    def get_colorschemes(self) -> tuple[str]:
        """Retrieve all available color schemes from the JSON file"""
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)
            return tuple(data.keys())
        except (FileNotFoundError, json.JSONDecodeError):
            return ()

    def create_colorscheme(self):
        # TODO: implement a function to create a new color scheme interactively
        ...
