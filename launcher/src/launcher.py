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
    if not venv_python.exists():
        venv_python = BACKEND_DIR / ".venv" / "bin" / "python"
    cmd = [str(venv_python), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    print(f"[launcher] Starting backend: {' '.join(cmd)}")
    return subprocess.Popen(cmd, cwd=str(BACKEND_DIR))


def start_frontend() -> subprocess.Popen:
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    cmd = [npm, "run", "dev"]
    print(f"[launcher] Starting frontend: {' '.join(cmd)}")
    return subprocess.Popen(cmd, cwd=str(FRONTEND_DIR))


def wait_for_health(timeout: int = HEALTH_TIMEOUT) -> bool:
    print(f"[launcher] Waiting for backend health at {HEALTH_URL} (timeout={timeout}s)...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=2) as resp:
                if resp.status == 200:
                    print("[launcher] Backend healthy.")
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(HEALTH_INTERVAL)
    print(f"[launcher] ERROR: Backend did not become healthy within {timeout}s.")
    return False


def open_browser(url: str) -> None:
    print(f"[launcher] Opening browser: {url}")
    webbrowser.open(url)


def terminate(proc: subprocess.Popen, name: str) -> None:
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print(f"[launcher] {name} stopped.")


def run() -> int:
    backend = None
    frontend = None
    try:
        backend = start_backend()
        frontend = start_frontend()

        if not wait_for_health():
            print("[launcher] Aborting: backend health check failed.")
            return 1

        open_browser(FRONTEND_URL)
        print("[launcher] POLYPRO running. Press Ctrl+C to stop.")

        backend.wait()
    except KeyboardInterrupt:
        print("\n[launcher] Shutting down...")
    finally:
        terminate(backend, "backend")
        terminate(frontend, "frontend")
    return 0


if __name__ == "__main__":
    sys.exit(run())
