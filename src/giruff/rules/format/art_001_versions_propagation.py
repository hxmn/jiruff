import logging

from giruff.base.services import JiraService

logger = logging.getLogger(__name__)


class FormatArt001VersionPropagation():
    def __init__(self, jira: JiraService) -> None:
        self._jira = jira

    def run(self) -> None:
        """
        Run the version propagation for ART-001.
        """
        issues_with_versions = self._jira.get_all_issues_by_jql(
            "fixVersion != EMPTY and issuetype in standardIssueTypes() and created >= -90d"
        )
        for issue in issues_with_versions:
            versions = issue.fields.fixVersions
            if len(versions) == 0:
                raise ValueError(
                    f"Issue {issue.key} has no fix versions set, but it should have at least one."
                )

            if len(versions) > 1:
                logger.warning("Issue %s has multiple fix versions set: %s", issue.key,
                               issue.fix_versions)

            version = versions[0]
            for child in self._jira.get_all_children(issue.key):
                if len(child.fields.fixVersions) >= 1:
                    continue
                logger.info("Setting fix version for child issue %s to %s", child.key, version)
                child.update(
                    fields={
                        "fixVersions": [{"id": version.id}],
                    },
                    notify=True,
                )