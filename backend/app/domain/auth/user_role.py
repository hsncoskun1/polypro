"""User role enum — v1.0.5."""
from enum import Enum

class UserRole(str, Enum):
    user = "user"
    admin = "admin"
