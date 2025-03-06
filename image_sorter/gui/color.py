import curses


def init_colors(
    default_colors: list[str] = None,
    colors: dict[str, tuple[int, int]] = None
) -> dict[str, int]:
    """Initialize terminal color palette"""
    default_colors = default_colors or {
        "foreground": curses.COLOR_WHITE,
        "background": curses.COLOR_BLACK,
    }
    colors = colors or {}

    curses.start_color()
    curses.use_default_colors()

    default_fg = default_colors.get("foreground", curses.COLOR_WHITE)
    default_bg = default_colors.get("background", curses.COLOR_BLACK)
    curses.init_pair(0, default_fg, default_bg)

    for color_id in range(1, curses.COLORS):
        curses.init_pair(color_id + 1, color_id, -1)

    return init_colorscheme_colors(colors)


def init_colorscheme_colors(colors: dict[str, tuple[int, int]]) -> dict[str, int]:
    """Initialize user-defined color pairs"""
    user_color_pairs: dict[str, int] = {}

    for color_name, (color_number, bg_number) in colors.items():
        bg_number = bg_number or -1

        if color_number is not None:
            curses.init_pair(color_number, color_number, bg_number)
            user_color_pairs[color_name] = color_number

    return user_color_pairs
