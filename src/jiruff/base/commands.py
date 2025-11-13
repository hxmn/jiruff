import abc
from argparse import Namespace
from pathlib import Path

from jiruff.base.services.cloud_jira import JiraService
from jiruff.config import Config
from jiruff.config import load_config
from jiruff.services.cloud_jira import CloudJiraService
from jiruff.services.local_jira import LocalJiraService


class BaseCommandHandler(abc.ABC):
    """
    Base class for command handlers.
    """

    command_name: str = "{command_name}"
    command_description: str = "{command_description}"

    def __init__(self):
        super().__init__()
        self.config: Config | None = None
        self.jira: JiraService | None = None
        self.local_jira: LocalJiraService | None = None

    def _load_config(self, args: Namespace) -> None:
        """
        Load configuration from command line arguments.
        This logic is common among all command handlers.

        :param args: Command line arguments.
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

    def _init_jira(self):
        jira_service = CloudJiraService()
        jira_service.auth(
            url=self.config.jira_url,
            username=self.config.jira_user,
            token=self.config.jira_token,
        )
        self.jira = jira_service

    def _init_local_jira(self):
        self.local_jira = LocalJiraService(
            local_dir_path=Path.home() / ".jiruff/issues" / self.config.company,
        )

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        """
        Method to handle the command.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: Result of the command execution.
        """
        pass
