"""v0.1.4 Live slice test — real subprocess backend + real HTTP health check.

Starts the actual uvicorn backend, polls /health until it responds 200,
then terminates cleanly. Browser open and frontend start stay mocked
(opening a real browser in CI is unsafe; npm dev server is slow to cold-start).
"""
import sys
import time
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import launcher

VENV_PYTHON = launcher.BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
HEALTH_URL = launcher.HEALTH_URL
STARTUP_TIMEOUT = 20  # seconds to wait for uvicorn


def _wait_http(url: str, timeout: int) -> bool:
    """Poll url until 200 or timeout. Returns True on success."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(0.5)
    return False


def test_backend_starts_and_health_responds():
    """Start real uvicorn backend, confirm /health returns 200, then shut it down."""
    cmd = [
        str(VENV_PYTHON), "-m", "uvicorn",
        "app.main:app", "--host", "127.0.0.1", "--port", "8000",
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=str(launcher.BACKEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        healthy = _wait_http(HEALTH_URL, STARTUP_TIMEOUT)
        assert healthy, (
            f"Backend did not respond at {HEALTH_URL} within {STARTUP_TIMEOUT}s"
        )

        # Confirm JSON body
        with urllib.request.urlopen(HEALTH_URL, timeout=3) as resp:
            import json
            body = json.loads(resp.read())
        assert body.get("status") == "ok", f"Unexpected body: {body}"

    finally:
        launcher.terminate(proc, "backend-live-test")


def test_run_with_real_health_mock_frontend():
    """run() flow: real backend starts, health passes, browser mocked, frontend mocked."""
    frontend_mock = MagicMock()
    frontend_mock.poll.return_value = None

    opened_urls = []

    def fake_open(url):
        opened_urls.append(url)

    # Override start_frontend so npm dev never actually runs
    with patch("launcher.start_frontend", return_value=frontend_mock), \
         patch("launcher.open_browser", side_effect=fake_open), \
         patch("launcher.terminate") as mock_term:

        # start_backend runs FOR REAL inside run() — but we need to intercept
        # it so we can terminate after the browser opens (avoid blocking wait())
        real_start_backend = launcher.start_backend
        backend_proc_holder = {}

        def capturing_start_backend():
            p = real_start_backend()
            backend_proc_holder["proc"] = p
            return p

        with patch("launcher.start_backend", side_effect=capturing_start_backend):
            # run() will block on backend.wait(); interrupt after browser opens
            import threading

            result_holder = {}

            def _run():
                result_holder["rc"] = launcher.run()

            t = threading.Thread(target=_run, daemon=True)
            t.start()

            # Wait until health passes and browser is opened
            deadline = time.time() + STARTUP_TIMEOUT + 5
            while time.time() < deadline:
                if opened_urls:
                    break
                time.sleep(0.5)

            # Kill the real backend so run() unblocks
            if "proc" in backend_proc_holder:
                launcher.terminate(backend_proc_holder["proc"], "live-test-backend")

            t.join(timeout=10)

    assert opened_urls, "Browser was never opened — health check may have failed"
    assert opened_urls[0] == launcher.FRONTEND_URL
