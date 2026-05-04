import subprocess
import time
import signal
import sys

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


def shutdown():
    print("\n⛔ Shutting down services...")
    for p in processes:
        p.terminate()
    sys.exit(0)


if __name__ == "__main__":
    print("🚀 Backend  → http://localhost:8000")
    print("🎨 Frontend → http://localhost:8501")

    p1 = start_backend()
    processes.append(p1)

    time.sleep(3)  # ensure backend starts first

    p2 = start_frontend()
    processes.append(p2)

    signal.signal(signal.SIGINT, lambda sig, frame: shutdown())
    signal.signal(signal.SIGTERM, lambda sig, frame: shutdown())

    for p in processes:
        p.wait()


# python run.py