import argparse
import sys
from argparse import Namespace

from jiruff.commands.check import CheckCommand
from jiruff.commands.format import FormatCommand


def main():
    parser = argparse.ArgumentParser(
        description="jiruff: linter for your GitLab and Jira"
    )

    subparsers = parser.add_subparsers(
        title="Commands", dest="command", required=True, help="Available commands"
    )

    # 'check' command parser
    check_command = CheckCommand()
    check_parser = subparsers.add_parser(
        name=check_command.command_name, help=check_command.command_description
    )
    check_parser.add_argument(
        "-c", "--config", required=False, help="TOML configuration file path"
    )
    check_parser.set_defaults(func=check_command)

    # 'format' command parser
    format_command = FormatCommand()

    fmt_parser = subparsers.add_parser(
        name=format_command.command_name, help=format_command.command_description
    )
    fmt_parser.add_argument(
        "-c", "--config", required=False, help="TOML configuration file path"
    )
    fmt_parser.set_defaults(func=format_command)

    # Parse arguments and dispatch
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
    logging.getLogger("keyring.backend").setLevel(logging.WARNING)

    main()
