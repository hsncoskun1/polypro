"""v0.1.4 Vertical slice integration tests — validates launcher ↔ backend ↔ frontend wiring."""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import subprocess

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import launcher


# ── Path wiring ──────────────────────────────────────────────────────────────

def test_backend_dir_exists():
    """Launcher ROOT resolves to an existing backend directory."""
    assert launcher.BACKEND_DIR.exists(), f"backend dir missing: {launcher.BACKEND_DIR}"


def test_frontend_dir_exists():
    """Launcher ROOT resolves to an existing frontend directory."""
    assert launcher.FRONTEND_DIR.exists(), f"frontend dir missing: {launcher.FRONTEND_DIR}"


def test_backend_entrypoint_exists():
    """app/main.py is present in the backend directory."""
    entrypoint = launcher.BACKEND_DIR / "app" / "main.py"
    assert entrypoint.exists(), f"backend entrypoint missing: {entrypoint}"


def test_frontend_entrypoint_exists():
    """src/main.tsx is present in the frontend directory."""
    entrypoint = launcher.FRONTEND_DIR / "src" / "main.tsx"
    assert entrypoint.exists(), f"frontend entrypoint missing: {entrypoint}"


# ── URL / health constants ────────────────────────────────────────────────────

def test_health_url_points_to_health_endpoint():
    """HEALTH_URL must end with /health."""
    assert launcher.HEALTH_URL.endswith("/health"), (
        f"Unexpected HEALTH_URL: {launcher.HEALTH_URL}"
    )


def test_health_url_uses_backend_url():
    """HEALTH_URL must be rooted at BACKEND_URL."""
    assert launcher.HEALTH_URL.startswith(launcher.BACKEND_URL)


def test_frontend_url_has_expected_port():
    """FRONTEND_URL must include port 5173 (Vite default)."""
    assert "5173" in launcher.FRONTEND_URL, (
        f"Unexpected FRONTEND_URL: {launcher.FRONTEND_URL}"
    )


# ── Full run() flow (mocked) ──────────────────────────────────────────────────

def test_run_opens_browser_on_healthy_backend():
    """run() should open the frontend URL when backend becomes healthy."""
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None
    mock_proc.wait.side_effect = KeyboardInterrupt

    with patch("launcher.start_backend", return_value=mock_proc), \
         patch("launcher.start_frontend", return_value=mock_proc), \
         patch("launcher.wait_for_health", return_value=True), \
         patch("launcher.open_browser") as mock_browser, \
         patch("launcher.terminate"):
        launcher.run()

    mock_browser.assert_called_once_with(launcher.FRONTEND_URL)


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


def test_run_terminates_both_procs_on_exit():
    """run() must call terminate() for both backend and frontend regardless of exit path."""
    backend_proc = MagicMock()
    frontend_proc = MagicMock()
    backend_proc.wait.side_effect = KeyboardInterrupt

    with patch("launcher.start_backend", return_value=backend_proc), \
         patch("launcher.start_frontend", return_value=frontend_proc), \
         patch("launcher.wait_for_health", return_value=True), \
         patch("launcher.open_browser"), \
         patch("launcher.terminate") as mock_term:
        launcher.run()

    names = [c.args[1] for c in mock_term.call_args_list]
    assert "backend" in names
    assert "frontend" in names
