from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class DiscoveryRunStatus:
    """Tracks the lifecycle state of the most recent discovery run.

    Updated by the trigger endpoint at run start, success, and error.
    Stored on app.state.discovery_run_status.
    """

    is_running: bool = False
    last_finished_at: datetime | None = None
    last_success_at: datetime | None = None
    last_result_summary: dict[str, Any] | None = None
    last_error: str | None = None
