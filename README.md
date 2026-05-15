# ChatBot-End_To-End-Application
An end-to-end chatbot application is a self-contained system that can handle a full conversation with a user, from interpreting the initial query to providing a final response or completing a requested task


# 🤖 AI Chatbot — End-to-End Application

A production-ready AI chatbot built with **FastAPI** (backend) and **Streamlit** (frontend), containerized with **Docker**, and deployed to **AWS EC2** via a fully automated **GitHub Actions** CI/CD pipeline.

---

## 📁 Project Structure

```
ChatBot-End_To-End-Application/
│
├── backend.py              # FastAPI backend — chat API + AWS Secrets Manager
├── frontend_app.py         # Streamlit frontend — chat UI
├── run.py                  # Local development launcher (runs both services)
├── supervisord.conf        # Supervisor config — runs backend + frontend in container
│
├── Dockerfile              # Docker image definition
├── .dockerignore           # Files excluded from Docker build
│
├── requirements.txt        # Production dependencies
├── requirements-test.txt   # Test-only dependencies (not in Docker image)
│
├── test_app.py             # Pytest test suite (27 tests, no real credentials needed)
│
├── .github/
│   └── workflows/
│       └── deploy.yml      # GitHub Actions CI/CD pipeline
│
└── README.md               # This file
```

---

## 🏗️ Architecture

```
User Browser
     │
     ▼
Streamlit Frontend  (port 8501)
     │  HTTP POST /chat
     ▼
FastAPI Backend     (port 8000)
     │
     ├──▶ AWS Secrets Manager  (OpenAI API key)
     │
     └──▶ OpenAI GPT-4o-mini
```

Both services run inside a **single Docker container** managed by **Supervisor**, deployed on an **AWS EC2** instance. The Docker image is stored in **Amazon ECR**.

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Frontend UI | Streamlit |
| LLM | OpenAI GPT-4o-mini via LangChain |
| Secret Management | AWS Secrets Manager |
| Containerization | Docker + Supervisor |
| Image Registry | Amazon ECR |
| Hosting | AWS EC2 |
| CI/CD | GitHub Actions |
| Testing | Pytest + HTTPX |

---

## 🚀 Quick Start — Local Development

### Prerequisites
- Python 3.11+
- An OpenAI API key

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/ChatBot-End_To-End-Application.git
cd ChatBot-End_To-End-Application
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your OpenAI API key

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-key-here
```

### 5. Run the application

```bash
python run.py
```

This starts both services together:
- **Frontend** → http://localhost:8501
- **Backend API** → http://localhost:8000
- **API Docs** → http://localhost:8000/docs

---

## 🧪 Running Tests

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

Run all 27 tests:

```bash
pytest test_app.py -v
```

Expected output:

```
collected 27 items

test_app.py::TestHealthCheck::test_health_returns_200 PASSED
test_app.py::TestHealthCheck::test_health_body PASSED
test_app.py::TestRoot::test_root_returns_200 PASSED
...
test_app.py::TestGetSecret::test_get_secret_returns_dict PASSED

27 passed in 5.92s
```

> ✅ No real AWS or OpenAI credentials are needed — all external services are mocked.

### Test Coverage

| Test Class | Tests | What's Verified |
|---|---|---|
| `TestHealthCheck` | 2 | `GET /health` returns 200 and correct body |
| `TestRoot` | 3 | `GET /` returns 200 and correct message |
| `TestChatEndpoint` | 10 | Chat responses, history, system prompt, edge cases |
| `TestChatErrorHandling` | 4 | LLM errors → 500, missing fields → 422 |
| `TestChatRequestModel` | 3 | Pydantic model defaults and validation |
| `TestCORS` | 2 | CORS headers present, preflight works |
| `TestGetSecret` | 3 | AWS Secrets Manager success and error paths |

---

## 🐳 Docker — Local Build & Run

Build the image:

```bash
docker build -t chatbot .
```

Run the container:

```bash
docker run -d \
  --name chatbot \
  -p 8000:8000 \
  -p 8501:8501 \
  -e OPENAI_API_KEY=sk-your-key-here \
  chatbot
```

Check health:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

View logs:

```bash
docker logs chatbot
```

Stop and remove:

```bash
docker stop chatbot && docker rm chatbot
```

---

## ☁️ AWS Deployment

### Prerequisites on AWS

1. **EC2 instance** — Amazon Linux 2 or Ubuntu, with Docker installed and GitHub Actions self-hosted runner configured
2. **ECR repository** — to store Docker images
3. **AWS Secrets Manager** — secret named `OpenAI-Keys` with the following structure:

```json
{
  "OPENAI_API_KEY": "sk-your-key-here"
}
```

4. **IAM Role or IAM User** — with permissions for `ecr:*` and `secretsmanager:GetSecretValue`

### GitHub Secrets Required

Go to your repo → **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | e.g. `us-east-1` |
| `ECR_REPOSITORY` | ECR repo name e.g. `chatbot` |

---

## 🔄 CI/CD Pipeline

Every push to `main` triggers the pipeline automatically:

```
Push to main
     │
     ▼
┌─────────────────────────────────┐
│   Continuous-Integration        │
│   (runs on: ubuntu-latest)      │
│                                 │
│  1. Checkout code               │
│  2. Set up Python 3.11          │
│  3. Install dependencies        │
│  4. ✅ Run 27 pytest tests      │  ← blocks deploy if tests fail
│  5. Configure AWS credentials   │
│  6. Login to ECR                │
│  7. Docker build & push to ECR  │
└─────────────────────────────────┘
     │  (only if all tests pass)
     ▼
┌─────────────────────────────────┐
│   Continuous-Deployment         │
│   (runs on: self-hosted EC2)    │
│                                 │
│  1. Pull latest image from ECR  │
│  2. Stop old container          │
│  3. Run new container           │
│  4. Wait for health check       │
│  5. Clean up old images         │
└─────────────────────────────────┘
```

---

## 🌐 API Reference

### `GET /health`
Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

---

### `GET /`
Root endpoint.

**Response:**
```json
{"message": "AI Chatbot API is running. POST to /chat to interact."}
```

---

### `POST /chat`
Send a message and get an AI reply.

**Request body:**
```json
{
  "message": "Hello, how are you?",
  "history": [
    {"role": "user", "content": "My name is Alice."},
    {"role": "assistant", "content": "Nice to meet you, Alice!"}
  ],
  "system_prompt": "You are a helpful AI assistant."
}
```

| Field | Type | Required | Default |
|---|---|---|---|
| `message` | string | ✅ Yes | — |
| `history` | list | No | `[]` |
| `system_prompt` | string | No | `"You are a helpful AI assistant."` |

**Response:**
```json
{"reply": "I'm doing well, thank you for asking!"}
```

**Error responses:**

| Status | Meaning |
|---|---|
| `422` | Missing or invalid request fields |
| `500` | LLM or internal server error |

---

## 📦 Dependencies

### `requirements.txt` (production)
```
fastapi
uvicorn
langchain
langchain-openai
python-dotenv
pydantic
boto3
requests
streamlit
```

### `requirements-test.txt` (CI only — not in Docker image)
```
pytest
pytest-asyncio
httpx
```

---

## 🔐 Security Notes

- The OpenAI API key is **never baked into the Docker image** — it is fetched at runtime from AWS Secrets Manager
- AWS credentials are passed as environment variables via GitHub Secrets
- The `.env` file is listed in `.dockerignore` and should also be in `.gitignore`
- CORS is currently set to `allow_origins=["*"]` — restrict this in production to your frontend domain

---

## 👤 Author

**Susant**

---

## 📄 License

This project is for educational and demonstration purposes.
