from enum import Enum


class RuleState(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WAITING = "waiting"
    DISABLED = "disabled"
    LOCKED_BY_ADMIN = "locked_by_admin"
