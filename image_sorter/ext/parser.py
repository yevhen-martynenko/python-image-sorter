import argparse


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
        "--input-dir",
        type=str,
        required=True,
        metavar="DIR",
        help="directory to take pictures from"
    )
    cmd.add_argument(
        "--output-dirs",
        required=True,
        nargs="*",
        metavar="DIR",
        help="directory to move pictures to"
    )
    cmd.add_argument(
        "--tree",
        action="store_true",
        default=False,
        help="first level tree"  # TODO: add help
    )
    cmd.add_argument(
        "--safe-delete",
        action="store_true",
        default=True,
        help="move files to '~/.trash/image_sorter/' instead of deleting them permanently"
    )
    cmd.add_argument(
        "--confirm-delete",
        action="store_true",
        default=False,
        help="require confirmation before deletion"
    )
    cmd.add_argument(
        "--auto-rename",
        type=int,
        nargs="?",
        metavar="BASE",
        # default="-1",
        help="automatically rename files using the specified numeral base"
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
