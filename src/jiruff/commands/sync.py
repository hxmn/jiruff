import logging
import time
from argparse import Namespace
from typing import Literal

import orjson

from jiruff.base.commands import BaseCommandHandler
from jiruff.local import load_local_state
from jiruff.local import save_local_state
from jiruff.local.paths import LOCAL_ISSUES_DIR
from jiruff.local.paths import LOCAL_TIMESHEET_DIR

logger = logging.getLogger(__name__)

TIMESHEET_BATCH_SIZE = 999
LEAST_TIMESHEET_ID = 20_000  # start timesheets series maybe empty

MAX_EMPTY_CONSECUTIVE_ISSUES = 2000


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

        self.download_timesheets()
        self.download_issues()

    def download_timesheets(self):
        logger.debug('Saving timesheets')

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

    def download_issues(self):
        logger.debug('Saving issues')

        local_state = load_local_state()
        issue_id = local_state.last_downloaded_issue_entry_id + 1
        num_of_empty_issues = 0

        while num_of_empty_issues < MAX_EMPTY_CONSECUTIVE_ISSUES:
            issue_path = LOCAL_ISSUES_DIR / self.config.company / f"{issue_id}.json"
            if not issue_path.parent.exists():
                issue_path.parent.mkdir(parents=True)
            issue_json = self.jira.get_full_issue_json(issue_id)

            if issue_json:
                logger.info(f"Issue is downloaded: {issue_json['id']}")
                issue_path.write_bytes(orjson.dumps(issue_json))
                num_of_empty_issues = 0
            else:
                num_of_empty_issues += 1

            issue_id += 1

            local_state.last_downloaded_issue_entry_id = issue_id - 1
            save_local_state(local_state)