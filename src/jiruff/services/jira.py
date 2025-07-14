import logging

from jira import JIRA

from jiruff.base.services import JiraService

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

    def get_all_issues_by_jql(self, jql: str):
        return self.jira.search_issues(jql_str=jql, maxResults=0)

    def get_all_children(self, key: str):
        return self.get_all_issues_by_jql(f"parent = {key}")
