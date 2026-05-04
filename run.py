import subprocess
import time
import signal
import sys
import requests

processes = []


def start_backend():
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "backend:app",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])


def start_frontend():
    return subprocess.Popen([
        sys.executable, "-m", "streamlit",
        "run", "frontend_app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])


def wait_for_backend(url: str, retries: int = 15, delay: float = 2.0) -> bool:
    """
    ✅ Poll the /health endpoint instead of using a fixed sleep.
    Returns True when the backend is ready, False if it never responds.
    """
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print(f"✅ Backend ready after {attempt} attempt(s).")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"   Waiting for backend... ({attempt}/{retries})")
        time.sleep(delay)
    return False


def shutdown(sig=None, frame=None):
    """✅ Graceful shutdown — terminates both processes cleanly."""
    print("\n⛔ Shutting down services...")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    # Give processes a moment to exit cleanly
    time.sleep(1)
    for p in processes:
        try:
            p.kill()   # force-kill if still running
        except Exception:
            pass
    sys.exit(0)


if __name__ == "__main__":
    print("🚀 Starting backend  → http://localhost:8000")
    p1 = start_backend()
    processes.append(p1)

    # ✅ Wait until backend /health responds instead of a blind sleep
    backend_ready = wait_for_backend("http://127.0.0.1:8000/health")
    if not backend_ready:
        print("❌ Backend did not start in time. Check logs above.")
        shutdown()

    print("🎨 Starting frontend → http://localhost:8501")
    p2 = start_frontend()
    processes.append(p2)

    # ✅ Register signal handlers AFTER both processes are started
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("\n✅ Both services are running.")
    print("   Backend  → http://localhost:8000")
    print("   Frontend → http://localhost:8501")
    print("   Press Ctrl+C to stop.\n")

    # Block until either process exits unexpectedly
    for p in processes:
        p.wait()

    print("⚠️  A service exited unexpectedly. Shutting down.")
    shutdown()



# python run.py