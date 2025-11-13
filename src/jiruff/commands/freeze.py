from argparse import Namespace
from typing import Literal

from jiruff import BaseCommandHandler


class FreezeCommand(BaseCommandHandler):
    """
    Command to format the code.
    """

    command_name: Literal["freeze"] = "freeze"
    command_description: str = (
        "Stop editing and time tracking for the task and all its children."
    )

    def __init__(self):
        super().__init__()

    def __call__(self, args: Namespace) -> None:
        print(args)