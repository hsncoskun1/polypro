"""Launcher smoke tests — v0.1.3"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import urllib.error

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from launcher import wait_for_health, terminate


def test_wait_for_health_success():
    """Returns True when health endpoint responds 200."""
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("launcher.urllib.request.urlopen", return_value=mock_resp):
        result = wait_for_health(timeout=5)
    assert result is True


def test_wait_for_health_timeout():
    """Returns False when health endpoint never responds."""
    with patch("launcher.urllib.request.urlopen", side_effect=urllib.error.URLError("refused")):
        with patch("launcher.time.sleep"):
            result = wait_for_health(timeout=1)
    assert result is False


def test_terminate_already_stopped():
    """terminate() handles already-stopped process gracefully."""
    proc = MagicMock()
    proc.poll.return_value = 0  # already stopped
    terminate(proc, "test")  # should not raise
