import abc
from typing import Callable


class JiraService(abc.ABC):
    @abc.abstractmethod
    def auth(self, server: str, user: str, token: str):
        pass

    @abc.abstractmethod
    def get_all_issues_by_jql(self, jql: str, num_results: int = 0):
        pass

    @abc.abstractmethod
    def get_all_children(self, key: str):
        pass

    @abc.abstractmethod
    def get_json(self, path: str, data: dict) -> dict:
        pass

    @abc.abstractmethod
    def get_full_issue_json(self, issue_id: int) -> dict:
        pass

    @abc.abstractmethod
    def add_watcher(self, issue_id: str, watcher_id: str):
        pass

    @abc.abstractmethod
    def get_all_issues(self, filter_func: Callable[[dict], bool]):
        pass