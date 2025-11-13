import logging
from typing import Literal

from pydantic import BaseModel
from pydantic import Field

from jiruff.base.services.cloud_jira import JiraService

logger = logging.getLogger(__name__)


class FormatIssues002Config(BaseModel):
    updated_history_depth: str = Field(
        default="-10d",
        description="Depth of the updated history to consider for version propagation.",
    )
    notify: bool = Field(
        default=False,
        description="Whether to notify users about the changes made during version propagation.",
    )


class FormatIssues002ChildParentAlignmentVersion:
    rule_key: Literal["issues-002"] = "issues-002"

    def __init__(
        self, jira: JiraService, rule_config: dict[str, str] | None = None
    ) -> None:
        self.jira = jira
        rule_config_dict: dict[str, str] = (
            rule_config if rule_config is not None else {}
        )
        self.rule_config = FormatIssues002Config(**rule_config_dict)

    def run(self) -> None:
        """
        Run the version alignment for ISSUES-002.
        """
        logger.info("Running ISSUES-002 version alignment formatter rule.")
        issues_with_versions = self.jira.get_all_issues_by_jql(
            f"fixVersion != EMPTY and "
            f"  issuetype in standardIssueTypes() and "
            f"  updated >= {self.rule_config.updated_history_depth}"
        )
        for issue in issues_with_versions:
            versions = issue.fields.fixVersions
            if len(versions) == 0:
                raise ValueError(
                    f"Issue {issue.key} has no fix versions set, but it should have at least one."
                )

            if len(versions) > 1:
                logger.warning(
                    "Issue %s has multiple fix versions set: %s",
                    issue.key,
                    issue.fields.fixVersions,
                )

            version = versions[0]
            for child in self.jira.get_all_children(issue.key):
                if len(child.fields.fixVersions) >= 1:
                    continue
                logger.info(
                    "Setting fix version for child issue %s to %s", child.key, version
                )
                child.update(
                    fields={
                        "fixVersions": [{"id": version.id}],
                    },
                    notify=self.rule_config.notify,
                )
