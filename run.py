"""
Local development launcher.
Starts the FastAPI backend and Streamlit frontend in two subprocesses,
waits for the backend to be ready, then keeps both alive until Ctrl-C.

Usage:
    python run.py
"""

import subprocess
import time
import signal
import sys
import requests

processes = []


def start_backend() -> subprocess.Popen:
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "backend:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",          # auto-reload on code changes locally
    ])


def start_frontend() -> subprocess.Popen:
    return subprocess.Popen([
        sys.executable, "-m", "streamlit",
        "run", "frontend_app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
    ])


def wait_for_backend(url: str, retries: int = 15, delay: float = 2.0) -> bool:
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print(f"Backend ready after {attempt} attempt(s).")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"   Waiting for backend... ({attempt}/{retries})")
        time.sleep(delay)
    return False


def shutdown(sig=None, frame=None) -> None:
    print("\nShutting down...")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    time.sleep(1)
    for p in processes:
        try:
            p.kill()
        except Exception:
            pass
    sys.exit(0)


if __name__ == "__main__":
    print("Starting backend  → http://localhost:8000")
    print("   API docs       → http://localhost:8000/docs")

    p1 = start_backend()
    processes.append(p1)

    if not wait_for_backend("http://127.0.0.1:8000/health"):
        print("Backend failed to start. Check errors above.")
        shutdown()

    print("Starting frontend → http://localhost:8501")
    p2 = start_frontend()
    processes.append(p2)

    signal.signal(signal.SIGINT,  shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("\nBoth services running.")
    print("   Open in browser → http://localhost:8501")
    print("   Press Ctrl+C to stop.\n")

    for p in processes:
        p.wait()

    print("A service exited unexpectedly.")
    shutdown()






# python run.py