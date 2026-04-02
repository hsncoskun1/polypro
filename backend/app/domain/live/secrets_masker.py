"""Secrets masking utility — v0.7.1.

Never logs or exposes secret values in plaintext.
"""

_NOT_SET = "NOT_SET"
_MASK_SUFFIX = "****"


def mask_secret(value: str) -> str:
    """Return a masked representation of a secret value.

    - Empty string → "NOT_SET"
    - 4 chars or fewer → "****"
    - More than 4 chars → first 4 chars + "****"
    """
    if not value:
        return _NOT_SET
    if len(value) <= 4:
        return _MASK_SUFFIX
    return value[:4] + _MASK_SUFFIX
