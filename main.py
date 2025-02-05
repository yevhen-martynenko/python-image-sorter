import curses
from curses.textpad import rectangle


def init_color():
    """Get the terminal color palette"""
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)


def main(stdscr):
    curses.curs_set(0)
    init_color()
    stdscr.bkgd(" ", curses.color_pair(8))
    stdscr.clear()

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

    stdscr.addstr(1, 2, "Column 1: files", curses.color_pair(8))
    stdscr.addstr(1, col2_x + 2, "Column 2: image", curses.color_pair(8))
    stdscr.addstr(1, col3_x + 2, "Column 3: dirs", curses.color_pair(8))

    stdscr.refresh()
    stdscr.getch()


curses.wrapper(main)
