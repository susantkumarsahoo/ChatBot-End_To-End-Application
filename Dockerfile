FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY backend.py .
COPY frontend_app.py .
COPY run.py .

# Expose both ports
EXPOSE 8000
EXPOSE 8501

# Start both servers via run.py
CMD ["python", "run.py"]