from pydantic import BaseModel
from pydantic import Field

from jiruff.local.paths import LOCAL_STATE_FILE


class LocalState(BaseModel):
    last_downloaded_timesheet_entry_id: int = Field(default=0)


def load_local_state() -> LocalState:
    if not LOCAL_STATE_FILE.exists():
        local_state = LocalState()
        LOCAL_STATE_FILE.write_text(local_state.model_dump_json())

    return LocalState.model_validate_json(LOCAL_STATE_FILE.read_bytes())

def save_local_state(state: LocalState):
    LOCAL_STATE_FILE.write_text(state.model_dump_json())