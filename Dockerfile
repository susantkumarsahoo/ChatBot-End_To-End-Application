FROM python:3.11-slim

# ✅ Install supervisord to manage multiple processes (backend + frontend)
#    and curl for the HEALTHCHECK below
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ✅ Upgrade pip first to avoid resolver warnings / outdated behaviour
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend.py .
COPY frontend_app.py .
COPY run.py .

# ✅ Supervisor config — manages both processes, restarts them if they crash
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000
EXPOSE 8501

# ✅ Health check — hits the /health endpoint we added to backend.py
#    Cloud platforms and docker-compose use this to know the container is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# ✅ Non-root user for security — never run containers as root in production
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# ✅ Use supervisord instead of run.py — it is the standard way to manage
#    multiple long-running processes inside a single container
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]



