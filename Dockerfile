FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    curl \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 appuser

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend.py .
COPY frontend_app.py .
COPY run.py .

COPY supervisord.conf /etc/supervisor/supervisord.conf

RUN chown -R appuser:appuser /app && \
    mkdir -p /home/appuser/.streamlit && \
    chown -R appuser:appuser /home/appuser/.streamlit

EXPOSE 8000
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]








# Dockerfile