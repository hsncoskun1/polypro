"""License status enum — v1.0.5."""
from enum import Enum

class LicenseStatus(str, Enum):
    active = "active"
    expired = "expired"
    inactive = "inactive"
