import logging
from typing import Literal

from pydantic import BaseModel
from pydantic import Field

from jiruff.base.services.cloud_jira import JiraService

logger = logging.getLogger(__name__)


class FormatIssues007AutoWatchRule(BaseModel):
    jira_user_id: str
    watch_all: bool = Field(default=False, description="Watch all issues.")


class FormatIssues007Config(BaseModel):
    auto_watch_rules: list[FormatIssues007AutoWatchRule]


class FormatIssues007AutoWatch:
    rule_key: Literal["issues-007"] = "issues-007"

    def __init__(
        self, jira: JiraService, rule_config: dict[str, str] | None = None
    ) -> None:
        self.jira = jira
        self.rule_config = FormatIssues007Config.model_validate(rule_config)

    def run(self) -> None:
        """
        Run the auto watch rule.
        """

        logger.info("Running ISSUES-007 auto watch rule")
        for auto_watch_rule in self.rule_config.auto_watch_rules:
            jira_user_id = auto_watch_rule.jira_user_id

            issues = self.jira.get_all_issues_by_jql(
                f"created >= -180d and watcher != '{jira_user_id}'"
            )
            for issue in issues:
                logger.info(f"auto watch issue: {issue.key} by {jira_user_id}")
                self.jira.add_watcher(issue.key, jira_user_id)
