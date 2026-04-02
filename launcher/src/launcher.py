"""POLYPRO Launcher — v0.1.5
Starts backend and frontend, waits for backend health, opens browser.
Hardened: pre-flight checks, clear error messages, clean shutdown.
"""
import subprocess
import sys
import time
import webbrowser
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent  # C:\POLYPRO
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:5173"
HEALTH_URL = f"{BACKEND_URL}/health"
HEALTH_TIMEOUT = 30  # seconds
HEALTH_INTERVAL = 1  # seconds


# ── Pre-flight checks ────────────────────────────────────────────────────────

def check_preflight() -> list[str]:
    """Return list of error strings; empty list means all clear."""
    errors: list[str] = []
    venv_python = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"

    if not BACKEND_DIR.exists():
        errors.append(f"backend directory not found: {BACKEND_DIR}")
    elif not venv_python.exists():
        errors.append(
            f"backend venv not found: {venv_python}\n"
            "  → Run: cd backend && python -m venv .venv && "
            ".venv/Scripts/pip install -r requirements.txt"
        )

    if not FRONTEND_DIR.exists():
        errors.append(f"frontend directory not found: {FRONTEND_DIR}")
    elif not (FRONTEND_DIR / "node_modules").exists():
        errors.append(
            f"frontend node_modules not found: {FRONTEND_DIR / 'node_modules'}\n"
            "  → Run: cd frontend && npm install"
        )

    return errors


# ── Process management ───────────────────────────────────────────────────────

def start_backend() -> subprocess.Popen:
    venv_python = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
    cmd = [str(venv_python), "-m", "uvicorn", "app.main:app",
           "--host", "127.0.0.1", "--port", "8000"]
    return subprocess.Popen(
        cmd,
        cwd=str(BACKEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def start_frontend() -> subprocess.Popen:
    return subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(FRONTEND_DIR),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def wait_for_health(url: str, timeout: int, interval: int) -> bool:
    """Poll url until 200 or timeout. Returns True on success."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(interval)
    return False


def open_browser(url: str) -> None:
    webbrowser.open(url)


def terminate(proc: subprocess.Popen, name: str) -> None:
    """Terminate a process, force-kill if it doesn't exit within 5s."""
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            print(f"[launcher] {name} force-killed after timeout", file=sys.stderr)


def _check_early_exit(proc: subprocess.Popen, name: str) -> bool:
    """Return True if process exited unexpectedly before we expected it."""
    code = proc.poll()
    if code is not None:
        print(
            f"[launcher] ERROR: {name} exited unexpectedly (code {code})",
            file=sys.stderr,
        )
        return True
    return False


# ── Main orchestration ───────────────────────────────────────────────────────

def run() -> int:
    # 1. Pre-flight
    errors = check_preflight()
    if errors:
        print("[launcher] Pre-flight check failed:", file=sys.stderr)
        for err in errors:
            print(f"  ✗ {err}", file=sys.stderr)
        return 1

    # 2. Start backend
    print("[launcher] Starting backend...")
    backend = start_backend()

    # Brief pause — let uvicorn fail fast if port is already in use
    time.sleep(0.5)
    if _check_early_exit(backend, "backend"):
        return 1

    # 3. Start frontend
    print("[launcher] Starting frontend...")
    frontend = start_frontend()

    # 4. Wait for backend health
    print(f"[launcher] Waiting for backend health ({HEALTH_TIMEOUT}s timeout)...")
    healthy = wait_for_health(HEALTH_URL, HEALTH_TIMEOUT, HEALTH_INTERVAL)

    if not healthy:
        print(
            f"[launcher] ERROR: backend did not respond at {HEALTH_URL} "
            f"within {HEALTH_TIMEOUT}s.\n"
            "  → Check backend logs for import errors or port conflicts.",
            file=sys.stderr,
        )
        terminate(backend, "backend")
        terminate(frontend, "frontend")
        return 1

    # 5. Open browser
    print(f"[launcher] Backend healthy. Opening {FRONTEND_URL}...")
    open_browser(FRONTEND_URL)

    # 6. Wait until interrupted or backend exits
    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\n[launcher] Interrupt received. Shutting down...")
    finally:
        terminate(backend, "backend")
        terminate(frontend, "frontend")
        print("[launcher] All processes stopped.")

    return 0


if __name__ == "__main__":
    sys.exit(run())
