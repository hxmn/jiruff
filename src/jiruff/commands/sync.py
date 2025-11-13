import logging
from argparse import Namespace
from datetime import datetime
from datetime import timedelta
from typing import Literal

import orjson

from jiruff.base.commands import BaseCommandHandler
from jiruff.local import load_local_state
from jiruff.local import save_local_state
from jiruff.local.paths import LOCAL_ISSUES_DIR
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
        logger.debug("Starting sync command")
        self._load_config(args)
        self._init_jira()

        self.download_timesheets()
        self.download_new_issues()
        # self.check_downloads()
        self.download_updated_issues()

    def download_timesheets(self):
        logger.info(f"Downloading {self.config.company} timesheets")

        local_state = load_local_state()
        start_id = local_state.last_downloaded_timesheet_entry_id

        while True:
            logger.debug(f"Downloading timesheets starting from ID {start_id}")
            ids = [str(i) for i in range(start_id, start_id + TIMESHEET_BATCH_SIZE)]
            timesheets_json = self.jira.get_json(
                path="/worklog/list", data={"ids": ids}
            )

            if len(timesheets_json) == 0 and start_id > LEAST_TIMESHEET_ID:
                logger.debug(f"Starting {start_id} timesheet list is empty.")
                break

            if len(timesheets_json) == 0 and start_id <= LEAST_TIMESHEET_ID:
                start_id += TIMESHEET_BATCH_SIZE
                continue

            for timesheet in timesheets_json:
                timesheet_id = int(timesheet["id"])
                file_path = (
                    LOCAL_TIMESHEET_DIR
                    / self.config.company
                    / str(timesheet_id // 1000)
                    / f"{timesheet_id}.json"
                )
                if not file_path.parent.exists():
                    file_path.parent.mkdir(parents=True)
                file_path.write_bytes(orjson.dumps(timesheet))

                start_id = timesheet_id + 1

        local_state.last_downloaded_timesheet_entry_id = start_id
        save_local_state(local_state)

    def download_new_issues(self):
        logger.info(f"Downloading {self.config.company} issues")

        latest_issue = self.jira.get_all_issues_by_jql(
            jql='created < now("-10000d") order by created DESC', num_results=1
        )
        max_issue_id = int(latest_issue[0].id)

        local_state = load_local_state()
        if local_state.last_downloaded_issue_entry_id == max_issue_id:
            logger.info("No new issues")
            return

        for issue_id in range(
            local_state.last_downloaded_issue_entry_id + 1, max_issue_id + 1
        ):
            self.download_issue(issue_id, update_local_state=False)

    def download_issue(self, issue_id: int, force=False, update_local_state=True):
        issue_path = LOCAL_ISSUES_DIR / self.config.company / f"{issue_id}.json"
        if not issue_path.parent.exists():
            issue_path.parent.mkdir(parents=True)
        if issue_path.exists() and not force:
            return

        logger.debug(f"Start downloading issue [{issue_id}]")
        issue_json = self.jira.get_full_issue_json(issue_id)

        if issue_json:
            logger.info(
                f"Issue is downloaded: {issue_json['key']}. {issue_json['fields']['summary']}"
            )
            issue_path.write_bytes(orjson.dumps(issue_json))

            local_state = load_local_state()
            if issue_id > local_state.last_downloaded_issue_entry_id:
                local_state.last_downloaded_issue_entry_id = issue_id
            if update_local_state:
                updated_at = datetime.fromisoformat(issue_json["fields"]["updated"])
                if (
                    isinstance(local_state.last_updated_issue_at, str)
                    or local_state.last_updated_issue_at < updated_at
                ):
                    local_state.last_updated_issue_at = updated_at
                save_local_state(local_state)

    def check_downloads(self):
        logger.debug(f"Checking {self.config.company} downloads")
        for timesheet_path in (LOCAL_TIMESHEET_DIR / self.config.company).rglob(
            "**/*.json"
        ):
            timesheet_json = orjson.loads(timesheet_path.read_bytes())
            issue_id = int(timesheet_json["issueId"])
            self.download_issue(issue_id, force=False)

    def download_updated_issues(self):
        logger.info(f"Downloading {self.config.company} updated issues")
        local_state = load_local_state()
        since = local_state.last_updated_issue_at
        if isinstance(since, datetime):
            since = since - timedelta(minutes=1)
            since = since.strftime("%Y-%m-%d %H:%M")
        updated_jql = f'updated > "{since}" order by updated desc'
        for issue in self.jira.get_all_issues_by_jql(updated_jql, num_results=0):
            issue_id = int(issue.id)
            self.download_issue(issue_id, force=True)
        logger.info(f"Finished downloading {self.config.company} updated issues")
