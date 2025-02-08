import argparse


def configure_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="image_sorter",
        description="sort and organize images efficiently",
        add_help=False,
        formatter_class=argparse.HelpFormatter
    )

    cmd_group = parser.add_argument_group("Commands")
    cmd = cmd_group.add_mutually_exclusive_group()
    cmd.add_argument(
        "-in",
        type=str,
        metavar="DIR",
        help="directory to take pictures from"
    )
    cmd.add_argument(
        "-out",
        type=str,
        metavar="DIR",
        help="directory to move pictures to"
    )
    cmd.add_argument(
        "--tree",
        type=str,
        nargs="?",
        metavar="00-11",
        help="first number refers to '-in', second to '-out'"
    )
    cmd.add_argument(
        "--safe-delete",
        action="store_true",
        help="move files to '~/.trash/image_sorter/' instead of deleting them permanently"
    )
    cmd.add_argument(
        "--confirm-delete",
        action="store_true",
        default=True,
        help="require confirmation before deletion"
    )
    cmd.add_argument(
        "--autorename",
        type=int,
        nargs="?",
        metavar="BASE",
        default="10",
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
