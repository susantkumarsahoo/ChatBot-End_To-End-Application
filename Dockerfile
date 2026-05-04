FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend.py .
COPY frontend_app.py .
COPY run.py .

EXPOSE 8000
EXPOSE 8501

CMD ["python", "run.py"]