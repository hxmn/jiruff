**jiruff** is the linter that helps you to maintain your software development process. It
integrates with GitLab and Jira to check and format issues, merge requests, and other items of your
workflow.

It has 4 simple command line arguments:

* `check` - check that your team follows the rules
* `format` - do some formatting and chores
* `repair` - do a set of tasks to maintain your infrastructure
* `report` - generate a report according to params

# implemented rules

## jira

### artifacts linter

* `art-001-versions-propagation` - if version is set in the issue, it should be in children issues