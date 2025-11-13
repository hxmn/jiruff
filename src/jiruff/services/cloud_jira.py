import json
import logging
from typing import Callable

from jira import JIRA
from jira import JIRAError

from jiruff.base.services.cloud_jira import JiraService

logger = logging.getLogger(__name__)


class CloudJiraService(JiraService):
    def __init__(self):
        self.jira: JIRA | None = None

    def auth(self, url: str, username: str, token: str):
        """
        Authenticate with the Jira server.
        :param url: Jira server URL.
        :param username: Username for authentication.
        :param token: API token for authentication.
        """
        if url is None or username is None or token is None:
            raise RuntimeError(f"url = {url}, username = {username}, token = {token}")

        if self.jira:
            return

        self.jira = JIRA(server=url, basic_auth=(username, token))

    def get_all_issues_by_jql(self, jql: str, num_results: int = 0):
        return self.jira.search_issues(jql_str=jql, maxResults=num_results)

    def get_all_children(self, key: str):
        return self.get_all_issues_by_jql(f"parent = {key}")

    def get_json(self, path: str, data: dict) -> dict:
        return self.jira._get_json(path, data, use_post=True)

    def get_full_issue_json(self, issue_id: int) -> dict | None:
        try:
            return self.jira.issue(
                id=str(issue_id), fields="*all", properties="*all"
            ).raw
        except JIRAError:
            return None

    def add_watcher(self, issue_id: str, watcher_id: str):
        # noinspection PyProtectedMember
        url = self.jira._get_url("issue/" + issue_id + "/watchers")
        # noinspection PyProtectedMember
        self.jira._session.post(url, data=json.dumps(watcher_id))

    def get_all_issues(self, filter_func: Callable[[dict], bool]):
        raise NotImplementedError()


