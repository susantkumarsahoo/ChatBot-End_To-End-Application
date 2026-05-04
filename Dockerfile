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

# Copy supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Give appuser ownership of /app
RUN chown -R appuser:appuser /app

EXPOSE 8000
EXPOSE 8501

# Health check hits the FastAPI /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# supervisord runs as root (it's a process manager — this is correct)
# It then spawns backend and frontend as 'appuser' (set in supervisord.conf)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]



