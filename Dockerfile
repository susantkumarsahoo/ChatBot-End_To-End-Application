FROM python:3.11-slim

# Install supervisord and curl (for HEALTHCHECK)
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Create non-root user early so we can set ownership
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend.py .
COPY frontend_app.py .
COPY run.py .

# Copy supervisord config to the standard Debian/Ubuntu location
# (/etc/supervisor/supervisord.conf is the file supervisord reads by default;
#  conf.d/ is for drop-in overrides — we write the full config to the main file
#  so both `supervisord` and `supervisord -c /etc/supervisor/supervisord.conf`
#  work identically)
COPY supervisord.conf /etc/supervisor/supervisord.conf

# Give appuser ownership of the app directory.
# /tmp is world-writable already, so the supervisord pidfile lands there safely.
RUN chown -R appuser:appuser /app

EXPOSE 8000
EXPOSE 8501

# Health check: FastAPI /health endpoint must return 200.
# --start-period gives the container 40 s to initialise before failures count.
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# supervisord runs as root (it is a process manager — this is correct).
# It spawns backend and frontend as 'appuser' (set in supervisord.conf).
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]








# Dockerfile