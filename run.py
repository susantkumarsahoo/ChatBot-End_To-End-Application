import subprocess
import sys
import time
import threading

def run_backend():
    subprocess.run([sys.executable, "-m", "uvicorn", "backend:app", "--port", "8000", "--reload"])

def run_frontend():
    time.sleep(2)  # wait for backend to start
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend_app.py", "--server.port", "8501"])

if __name__ == "__main__":
    print("🚀 Starting Backend  → http://localhost:8000")
    print("🎨 Starting Frontend → http://localhost:8501")

    t1 = threading.Thread(target=run_backend, daemon=True)
    t2 = threading.Thread(target=run_frontend, daemon=True)

    t1.start()
    t2.start()

    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        print("\n⛔ Shutting down both servers...")


# python run.py