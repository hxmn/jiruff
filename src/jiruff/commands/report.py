from argparse import Namespace
from typing import Literal

from jiruff import BaseCommandHandler


class ReportCommand(BaseCommandHandler):
    command: Literal["report"] = "report"
    command_description: str = "Report according to some rules"

    def __init__(self):
        super().__init__()

    def __call__(self, args: Namespace):
        """
        Method to handle the format command.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: Result of the command execution.
        """
        self._load_config(args)
        self._init_jira()
