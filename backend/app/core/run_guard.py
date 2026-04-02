import threading


class DiscoveryRunGuard:
    """Thread-safe guard that allows at most one concurrent discovery run.

    acquire() returns True if the lock was acquired (caller may proceed).
    acquire() returns False if a run is already in progress.
    release() must be called by the caller when the run finishes.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()

    def acquire(self) -> bool:
        return self._lock.acquire(blocking=False)

    def release(self) -> None:
        self._lock.release()
