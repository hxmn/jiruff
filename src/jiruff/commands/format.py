from argparse import Namespace
from typing import Literal

from jiruff.base.commands import BaseCommandHandler
from jiruff.rules.format.issues_001_versions_propagation import (
    FormatIssues001VersionPropagation,
)
from jiruff.rules.format.issues_007_auto_watch import FormatIssues007AutoWatch


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

        issues_001 = FormatIssues001VersionPropagation(
            jira=self.jira,
            rule_config=self.config.get_config_dict(FormatIssues001VersionPropagation.rule_key)
        )
        issues_001.run()

        issues_007 = FormatIssues007AutoWatch(
            jira=self.jira,
            rule_config=self.config.get_config_dict(FormatIssues007AutoWatch.rule_key)
        )
        issues_007.run()
