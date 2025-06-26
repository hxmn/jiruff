import abc

from jira import JIRA


class JiraService(abc.ABC):
    @abc.abstractmethod
    def auth(self, server: str, user: str, token: str):
        pass

    @abc.abstractmethod
    def get_all_issues_by_jql(self, jql: str):
        pass

    @abc.abstractmethod
    def get_all_children(self, key: str):
        pass
