import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import urllib.error

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import launcher


def test_wait_for_health_success():
    """Returns True when URL responds 200 on first attempt."""
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.status = 200

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = launcher.wait_for_health("http://test", timeout=5, interval=0)

    assert result is True


def test_wait_for_health_timeout():
    """Returns False when URL never responds within timeout."""
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused")):
        result = launcher.wait_for_health("http://test", timeout=0.1, interval=0)

    assert result is False


def test_terminate_already_stopped():
    """terminate() is safe when process already exited."""
    mock_proc = MagicMock()
    mock_proc.poll.return_value = 0  # already done

    launcher.terminate(mock_proc, "test-proc")

    mock_proc.terminate.assert_not_called()


def test_path_constants():
    """ROOT resolves to an existing directory."""
    assert launcher.BACKEND_DIR.parent == launcher.ROOT
    assert launcher.FRONTEND_DIR.parent == launcher.ROOT
    assert launcher.HEALTH_URL == f"{launcher.BACKEND_URL}/health"


def test_run_aborts_when_backend_unhealthy():
    """run() returns non-zero and skips browser when health check fails."""
    mock_proc = MagicMock()

    with patch("launcher.start_backend", return_value=mock_proc), \
         patch("launcher.start_frontend", return_value=mock_proc), \
         patch("launcher.wait_for_health", return_value=False), \
         patch("launcher.open_browser") as mock_browser, \
         patch("launcher.terminate"):
        result = launcher.run()

    assert result != 0
    mock_browser.assert_not_called()
