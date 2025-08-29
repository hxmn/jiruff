from pathlib import Path

JIRUFF_PATH = Path.home() / ".jiruff"

LOCAL_STATE_FILE = JIRUFF_PATH / "local_state.json"
if not LOCAL_STATE_FILE.parent.exists():
    LOCAL_STATE_FILE.parent.mkdir(parents=True)

LOCAL_TIMESHEET_DIR = JIRUFF_PATH / "timesheets"
if not LOCAL_TIMESHEET_DIR.exists():
    LOCAL_TIMESHEET_DIR.mkdir(parents=True)

LOCAL_ISSUES_DIR = JIRUFF_PATH / "issues"
if not LOCAL_ISSUES_DIR.exists():
    LOCAL_ISSUES_DIR.mkdir(parents=True)
