import argparse
import sys
from typing import Type

from jiruff.base.commands import BaseCommandHandler
from jiruff.commands.check import CheckCommand
from jiruff.commands.format import FormatCommand
from jiruff.commands.sync import SyncCommand


def add_command(
        command: Type[BaseCommandHandler],
        subparsers: argparse._SubParsersAction,
) -> None:
    parser = subparsers.add_parser(
        name=command.command_name,
        help=command.command_description
    )
    parser.add_argument(
        "-c", "--config", required=False, help="TOML configuration file",
    )
    parser.set_defaults(func=command())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="jiruff: linter for your GitLab and Jira"
    )
    parser.add_argument(
        "-V", "--verbose", help="Verbose output", action="store_true"
    )

    subparsers = parser.add_subparsers(
        title="Commands", dest="command", required=True, help="Available commands"
    )
    add_command(CheckCommand, subparsers)
    add_command(FormatCommand, subparsers)
    add_command(SyncCommand, subparsers)


    # Parse arguments and dispatch
    args = parser.parse_args()

    import logging

    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(asctime)s - %(message)s - [%(name)s]",
        stream=sys.stdout,
    )
    logging.getLogger("keyring.backend").setLevel(logging.WARNING)


    args.func(args)


if __name__ == "__main__":
    main()
