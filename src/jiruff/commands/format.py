from argparse import Namespace
from pathlib import Path
from typing import Literal

from jiruff.base.commands import BaseCommandHandler
from jiruff.config import Config
from jiruff.config import load_config
from jiruff.rules.format.art_001_versions_propagation import (
    FormatArt001VersionPropagation,
)
from jiruff.services.jira import CloudJiraService


class FormatCommand(BaseCommandHandler):
    """
    Command to format the code.
    """

    command_name: Literal["format"] = "format"
    command_description: str = (
        "Format gitlab and jira instance according to the configuration."
    )

    def __init__(self):
        self.config: Config | None = None

    def __call__(self, args: Namespace) -> None:
        """
        Method to handle the format command.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: Result of the command execution.
        """
        if hasattr(args, "config") and args.config:
            config_path = Path(args.config)
            if config_path.exists():
                self.config = load_config(config_path)
            else:
                raise FileNotFoundError(
                    f"Configuration file '{config_path}' not found."
                )
        else:
            self.config = load_config()

        jira_service = CloudJiraService()
        jira_service.auth(
            url=self.config.jira_url,
            username=self.config.jira_user,
            token=self.config.jira_token,
        )

        art_001 = FormatArt001VersionPropagation(
            jira=jira_service,
            rule_config=self.config.get_config_dict(FormatArt001VersionPropagation.rule_key)
        )
        art_001.run()
