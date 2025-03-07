import argparse

# TODO: implement dynamic argument completion with `argcomplete` for tab completion support


def configure_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="image_sorter",
        description="sort and organize images efficiently",
        add_help=False,
        formatter_class=argparse.HelpFormatter
    )

    cmd_group = parser.add_argument_group("Commands")
    cmd = cmd_group
    cmd.add_argument(
        "-i", "--input-dir",
        type=str,
        metavar="DIR",
        help="directory to take pictures from"
    )
    cmd.add_argument(
        "-o", "--output-dirs",
        nargs="*",
        metavar="DIR",
        help="directories to move pictures to"
    )
    cmd.add_argument(
        "-t", "--tree",
        action="store_true",
        default=False,
        help="list all files in the first level of the target directory tree"
    )
    cmd.add_argument(
        "-c", "--copy_mode",
        action="store_true",
        default=False,
        help="enable copy mode instead of moving files"
    )
    cmd.add_argument(
        "--safe-delete",
        action="store_true",
        default=True,
        help="move files to '~/.trash/image_sorter/' instead of deleting them permanently"
    )
    cmd.add_argument(
        "-r", "--auto-rename",
        type=int,
        nargs="?",
        metavar="BASE",
        default="0",
        help="automatically rename files using the specified numeral base"
    )
    cmd.add_argument(
        "--theme",
        type=str,
        default="default",
        help="specify the color theme to use"
    )

    opt_group = parser.add_argument_group("Options")
    opt = opt_group.add_mutually_exclusive_group()
    opt.add_argument(
        "-h", "--help",
        action="store_true",
        help="show this screen"
    )
    opt.add_argument(
        "-v", "--version",
        action="store_true",
        help="show version information"
    )

    return parser
