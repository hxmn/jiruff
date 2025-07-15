import logging
from argparse import Namespace
from typing import Literal

import orjson

from jiruff.base.commands import BaseCommandHandler
from jiruff.local import load_local_state
from jiruff.local import save_local_state
from jiruff.local.paths import LOCAL_TIMESHEET_DIR

logger = logging.getLogger(__name__)

TIMESHEET_BATCH_SIZE = 999
LEAST_TIMESHEET_ID = 20_000


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

        self.save_timesheets()

    def save_timesheets(self):
        local_state = load_local_state()
        start_id = local_state.last_downloaded_timesheet_entry_id

        while True:
            ids = [str(i) for i in range(start_id, start_id + TIMESHEET_BATCH_SIZE)]
            timesheets_json = self.jira.get_json(
                path="/worklog/list", data={"ids": ids})

            if len(timesheets_json) == 0 and start_id > LEAST_TIMESHEET_ID:
                logger.debug(f"Starting {start_id} timesheet list is empty.")
                break

            for timesheet in timesheets_json:
                timesheet_id = int(timesheet['id'])
                file_path = (LOCAL_TIMESHEET_DIR / self.config.company /
                             str(timesheet_id // 1000) / f"{timesheet_id}.json")
                if not file_path.parent.exists():
                    file_path.parent.mkdir(parents=True)
                file_path.write_bytes(orjson.dumps(timesheet))

                start_id = timesheet_id + 1

        local_state.last_downloaded_timesheet_entry_id = start_id
        save_local_state(local_state)
