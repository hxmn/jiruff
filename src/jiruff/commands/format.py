from argparse import Namespace
from typing import Literal

from jiruff.base.commands import BaseCommandHandler
from jiruff.rules.format.art_001_versions_propagation import (
    FormatArt001VersionPropagation,
)


class FormatCommand(BaseCommandHandler):
    """
    Command to format the code.
    """

    command_name: Literal["format"] = "format"
    command_description: str = (
        "Format gitlab and jira instance according to the configuration."
    )

    def __init__(self):
        super().__init__()

    def __call__(self, args: Namespace) -> None:
        """
        Method to handle the format command.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: Result of the command execution.
        """
        self._load_config(args)
        self._init_jira()

        art_001 = FormatArt001VersionPropagation(
            jira=self.jira,
            rule_config=self.config.get_config_dict(FormatArt001VersionPropagation.rule_key)
        )
        art_001.run()
