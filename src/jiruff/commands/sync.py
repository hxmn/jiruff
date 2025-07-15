import logging
from argparse import Namespace
from typing import Literal

from jiruff.base.commands import BaseCommandHandler

logger = logging.getLogger(__name__)


class SyncCommand(BaseCommandHandler):
    """
    Command to synchronize data between GitLab and Jira.
    """

    command_name: Literal["sync"] = "sync"
    command_description: str = "Synchronize data between GitLab and Jira instances."

    def __init__(self):
        super().__init__()

    def __call__(self, args: Namespace):
        """
        Method to handle the sync command.
        :param args: Positional arguments.
        :param kwargs: Keyword arguments.
        :return: Result of the command execution.
        """
        logger.debug('Starting sync command')
        self._load_config(args)
        self._init_jira()
