"""Admin-controlled general visibility policy.

Covers event, panel, and feature visibility targets.
Rule visibility is handled separately in rule_policy.py.
Admin defines which targets are visible; default is visible=True.
"""
from dataclasses import dataclass, field
from enum import Enum


class VisibilityTargetType(str, Enum):
    EVENT = "event"
    PANEL = "panel"
    FEATURE = "feature"


@dataclass
class VisibilityEntry:
    target_type: VisibilityTargetType
    target_name: str
    visible: bool = True


@dataclass
class AdminVisibilityPolicy:
    entries: dict[str, VisibilityEntry] = field(default_factory=dict)

    def is_visible(self, target_type: VisibilityTargetType, target_name: str) -> bool:
        """Return visibility for a target. Defaults to True if not explicitly set."""
        key = f"{target_type.value}:{target_name}"
        entry = self.entries.get(key)
        return entry.visible if entry is not None else True

    def set_visibility(
        self,
        target_type: VisibilityTargetType,
        target_name: str,
        visible: bool,
    ) -> None:
        key = f"{target_type.value}:{target_name}"
        self.entries[key] = VisibilityEntry(
            target_type=target_type,
            target_name=target_name,
            visible=visible,
        )
