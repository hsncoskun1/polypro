"""POLYPRO Launcher — v0.1.3
Starts backend and frontend, waits for backend health, opens browser.
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


def start_backend() -> subprocess.Popen:
    venv_python = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
    cmd = [str(venv_python), "-m", "uvicorn", "app.main:app",
           "--host", "127.0.0.1", "--port", "8000"]
    return subprocess.Popen(cmd, cwd=str(BACKEND_DIR))


def start_frontend() -> subprocess.Popen:
    cmd = ["npm", "run", "dev"]
    return subprocess.Popen(cmd, cwd=str(FRONTEND_DIR), shell=True)


def wait_for_health(url: str, timeout: int, interval: int) -> bool:
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
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            print(f"[launcher] {name} force-killed", file=sys.stderr)


def run() -> int:
    print("[launcher] Starting backend...")
    backend = start_backend()

    print("[launcher] Starting frontend...")
    frontend = start_frontend()

    print(f"[launcher] Waiting for backend health at {HEALTH_URL}...")
    healthy = wait_for_health(HEALTH_URL, HEALTH_TIMEOUT, HEALTH_INTERVAL)

    if not healthy:
        print(f"[launcher] ERROR: backend did not respond within {HEALTH_TIMEOUT}s",
              file=sys.stderr)
        terminate(backend, "backend")
        terminate(frontend, "frontend")
        return 1

    print(f"[launcher] Backend healthy. Opening {FRONTEND_URL}...")
    open_browser(FRONTEND_URL)

    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\n[launcher] Shutting down...")
    finally:
        terminate(backend, "backend")
        terminate(frontend, "frontend")

    return 0


if __name__ == "__main__":
    sys.exit(run())
