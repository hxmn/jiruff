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
        Authenticate with the Jira server. Challenges the credentials with a
        ``myself()`` call so a bad auth scheme fails here rather than later.

        Tries Bearer PAT (Data Center) first, then Basic (Cloud email+API token).
        """
        if url is None or username is None or token is None:
            raise RuntimeError(f"url = {url}, username = {username}, token = {token}")

        if self.jira:
            return

        last_err: JIRAError | None = None
        for label, kwargs in (
            ("bearer", {"token_auth": token}),
            ("basic", {"basic_auth": (username, token)}),
        ):
            try:
                jira = JIRA(server=url, **kwargs)
                jira.myself()
            except JIRAError as e:
                if e.status_code in (401, 403):
                    logger.debug(f"JIRA {label} auth rejected: HTTP {e.status_code}")
                    last_err = e
                    # CAPTCHA lockout: every Basic attempt prolongs it. Stop now
                    # and surface a clear error so the user logs in via browser.
                    if "CAPTCHA_CHALLENGE" in (e.text or ""):
                        raise RuntimeError(
                            "JIRA login is CAPTCHA-locked for this account. "
                            "Open the login page in a browser and solve the CAPTCHA, "
                            "then retry. Login URL is in the response: " + e.text
                        ) from e
                    continue
                raise
            logger.debug(f"JIRA auth succeeded via {label}")
            self.jira = jira
            return

        assert last_err is not None
        raise last_err

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


