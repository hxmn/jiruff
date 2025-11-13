from pathlib import Path
from typing import Callable

from jiruff.base.services.cloud_jira import JiraService


class LocalJiraService(JiraService):
    def __init__(self, local_dir_path: Path):
        super().__init__()
        self._local_dir_path = local_dir_path
        if not self._local_dir_path.exists():
            raise FileNotFoundError("Local directory should exist before using LocalJiraService")

    def auth(self, server: str, user: str, token: str):
        raise NotImplementedError()

    def get_all_issues_by_jql(self, jql: str, num_results: int = 0):
        raise NotImplementedError()

    def get_all_children(self, key: str):
        raise NotImplementedError()

    def get_json(self, path: str, data: dict) -> dict:
        raise NotImplementedError()

    def get_full_issue_json(self, issue_id: int) -> dict:
        raise NotImplementedError()

    def add_watcher(self, issue_id: str, watcher_id: str):
        raise NotImplementedError()

    def get_all_issues(self, filter_func: Callable[[dict], bool]):
        pass

