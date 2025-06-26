import argparse
import sys
from argparse import Namespace

from giruff.commands.format import FormatCommand


def check_command(args: Namespace):
    """
    Placeholder for the 'check' command logic.
    For example, this could verify file integrity or run validations.
    """
    target = args.target
    # Example implementation: check if the target exists and is non-empty
    try:
        with open(target, 'r') as f:
            data = f.read()
            if not data:
                print(f"Error: '{target}' is empty.", file=sys.stderr)
                sys.exit(1)
            print(f"Check passed: '{target}' is non-empty.")
    except FileNotFoundError:
        print(f"Error: '{target}' not found.", file=sys.stderr)
        sys.exit(1)



def main():
    parser = argparse.ArgumentParser(
        description="giruff: linter for your GitLab and Jira"
    )

    subparsers = parser.add_subparsers(
        title='Commands',
        dest='command',
        required=True,
        help='Available commands'
    )

    # 'check' command parser
    check_parser = subparsers.add_parser(
        'check', help="Run checks on a target file"
    )
    check_parser.add_argument(
        '-c', '--config', required=False,
        help="TOML configuration file path"
    )
    check_parser.set_defaults(func=check_command)

    # 'format' command parser
    format_command = FormatCommand()

    fmt_parser = subparsers.add_parser(
        name=format_command.command_name,
        help=format_command.command_description
    )
    fmt_parser.add_argument(
        '-c', '--config', required=False,
        help="TOML configuration file path"
    )
    fmt_parser.set_defaults(func=format_command)

    # Parse arguments and dispatch
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()