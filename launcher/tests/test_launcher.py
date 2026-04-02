import sys
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import urllib.error

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import launcher


# ── wait_for_health ───────────────────────────────────────────────────────────

def test_wait_for_health_success():
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.status = 200
    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert launcher.wait_for_health("http://test", timeout=5, interval=0) is True


def test_wait_for_health_timeout():
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("refused")):
        assert launcher.wait_for_health("http://test", timeout=0.1, interval=0) is False


# ── terminate ────────────────────────────────────────────────────────────────

def test_terminate_already_stopped():
    proc = MagicMock()
    proc.poll.return_value = 0
    launcher.terminate(proc, "test")
    proc.terminate.assert_not_called()


def test_terminate_force_kill_on_timeout():
    proc = MagicMock()
    proc.poll.return_value = None
    proc.wait.side_effect = subprocess.TimeoutExpired(cmd="x", timeout=5)
    launcher.terminate(proc, "stubborn")
    proc.kill.assert_called_once()


# ── check_preflight ──────────────────────────────────────────────────────────

def test_preflight_passes_with_real_dirs():
    """Preflight passes when backend and frontend dirs + venv + node_modules exist."""
    errors = launcher.check_preflight()
    assert errors == [], f"Unexpected preflight errors: {errors}"


def test_preflight_fails_missing_backend(tmp_path):
    with patch.object(launcher, "BACKEND_DIR", tmp_path / "no_backend"), \
         patch.object(launcher, "FRONTEND_DIR", tmp_path / "no_frontend"):
        errors = launcher.check_preflight()
    assert any("backend" in e for e in errors)
    assert any("frontend" in e for e in errors)


def test_preflight_fails_missing_venv(tmp_path):
    backend = tmp_path / "backend"
    backend.mkdir()
    frontend = tmp_path / "frontend"
    (frontend / "node_modules").mkdir(parents=True)
    with patch.object(launcher, "BACKEND_DIR", backend), \
         patch.object(launcher, "FRONTEND_DIR", frontend):
        errors = launcher.check_preflight()
    assert any("venv" in e for e in errors)


def test_preflight_fails_missing_node_modules(tmp_path):
    backend = tmp_path / "backend"
    venv_scripts = backend / ".venv" / "Scripts"
    venv_scripts.mkdir(parents=True)
    (venv_scripts / "python.exe").touch()
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    with patch.object(launcher, "BACKEND_DIR", backend), \
         patch.object(launcher, "FRONTEND_DIR", frontend):
        errors = launcher.check_preflight()
    assert any("node_modules" in e for e in errors)


# ── _check_early_exit ─────────────────────────────────────────────────────────

def test_check_early_exit_detects_crash():
    proc = MagicMock()
    proc.poll.return_value = 1
    assert launcher._check_early_exit(proc, "backend") is True


def test_check_early_exit_ok_when_running():
    proc = MagicMock()
    proc.poll.return_value = None
    assert launcher._check_early_exit(proc, "backend") is False


# ── run() flow ────────────────────────────────────────────────────────────────

def test_run_aborts_on_preflight_failure():
    with patch("launcher.check_preflight", return_value=["missing backend"]):
        assert launcher.run() == 1


def test_run_aborts_when_backend_unhealthy():
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    with patch("launcher.check_preflight", return_value=[]), \
         patch("launcher.start_backend", return_value=mock_proc), \
         patch("launcher.start_frontend", return_value=mock_proc), \
         patch("launcher.wait_for_health", return_value=False), \
         patch("launcher.open_browser") as mock_browser, \
         patch("launcher.terminate"):
        assert launcher.run() != 0
    mock_browser.assert_not_called()


def test_run_aborts_when_backend_exits_early():
    crashed = MagicMock()
    crashed.poll.return_value = 1  # crashed immediately
    with patch("launcher.check_preflight", return_value=[]), \
         patch("launcher.start_backend", return_value=crashed), \
         patch("launcher.open_browser") as mock_browser:
        result = launcher.run()
    assert result != 0
    mock_browser.assert_not_called()


def test_run_opens_browser_when_healthy():
    proc = MagicMock()
    proc.poll.return_value = None
    proc.wait.side_effect = KeyboardInterrupt
    with patch("launcher.check_preflight", return_value=[]), \
         patch("launcher.start_backend", return_value=proc), \
         patch("launcher.start_frontend", return_value=proc), \
         patch("launcher.wait_for_health", return_value=True), \
         patch("launcher.open_browser") as mock_browser, \
         patch("launcher.terminate"):
        launcher.run()
    mock_browser.assert_called_once_with(launcher.FRONTEND_URL)


def test_run_terminate_called_on_both_processes():
    """terminate() is called for both backend and frontend on shutdown."""
    proc = MagicMock()
    proc.poll.return_value = None
    proc.wait.side_effect = KeyboardInterrupt
    with patch("launcher.check_preflight", return_value=[]), \
         patch("launcher.start_backend", return_value=proc), \
         patch("launcher.start_frontend", return_value=proc), \
         patch("launcher.wait_for_health", return_value=True), \
         patch("launcher.open_browser"), \
         patch("launcher.terminate") as mock_terminate:
        launcher.run()
    assert mock_terminate.call_count == 2


def test_run_terminate_called_on_unhealthy_backend():
    """Both processes are terminated when backend health check fails."""
    backend = MagicMock()
    backend.poll.return_value = None
    frontend = MagicMock()
    frontend.poll.return_value = None
    with patch("launcher.check_preflight", return_value=[]), \
         patch("launcher.start_backend", return_value=backend), \
         patch("launcher.start_frontend", return_value=frontend), \
         patch("launcher.wait_for_health", return_value=False), \
         patch("launcher.terminate") as mock_terminate:
        launcher.run()
    assert mock_terminate.call_count == 2


def test_run_aborts_when_frontend_exits_early():
    """run() aborts and terminates backend when frontend exits early."""
    backend = MagicMock()
    backend.poll.return_value = None
    frontend_crashed = MagicMock()
    frontend_crashed.poll.return_value = 1  # crashed immediately
    with patch("launcher.check_preflight", return_value=[]), \
         patch("launcher.start_backend", return_value=backend), \
         patch("launcher.start_frontend", return_value=frontend_crashed), \
         patch("launcher.open_browser") as mock_browser, \
         patch("launcher.terminate") as mock_terminate:
        result = launcher.run()
    assert result != 0
    mock_browser.assert_not_called()
    mock_terminate.assert_called()
