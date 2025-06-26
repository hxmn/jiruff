from argparse import Namespace
from pathlib import Path

from giruff.base.commands import BaseCommandHandler
from giruff.config import Config
from giruff.config import load_config
from giruff.rules.format.art_001_versions_propagation import FormatArt001VersionPropagation
from giruff.services.jira import CloudJiraService


class FormatCommand(BaseCommandHandler):
    """
    Command to format the code.
    """
    command_name: str = "format"
    command_description: str = "Format gitlab and jira instance according to the configuration."

    def __init__(self):
        self.config: Config | None = None

    def __call__(self, args: Namespace) -> None:
        """
        Method to handle the format command.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: Result of the command execution.
        """
        if hasattr(args, 'config') and args.config:
            config_path = Path(args.config)
            if config_path.exists():
                self.config = load_config(config_path)
            else:
                raise FileNotFoundError(f"Configuration file '{config_path}' not found.")

        jira_service = CloudJiraService()
        jira_service.auth(
            url=self.config.jira_url,
            username=self.config.jira_user,
            token=self.config.jira_token
        )

        art_001 = FormatArt001VersionPropagation(jira=jira_service)
        art_001.run()