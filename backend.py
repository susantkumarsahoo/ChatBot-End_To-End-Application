from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import boto3
import json
import os

load_dotenv()  # works locally; no-op in Docker (no .env file present)

# ─────────────────────────────────────────
# AWS Secrets Manager
# ─────────────────────────────────────────
def get_secret(secret_name: str, region: str) -> dict:
    """Retrieve a JSON secret from AWS Secrets Manager."""
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region)
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise RuntimeError(f"Failed to retrieve secret '{secret_name}': {e}")
    return json.loads(response["SecretString"])


# ─────────────────────────────────────────
# Resolve OpenAI API key
# Priority: AWS Secrets Manager → env var
# ─────────────────────────────────────────
AWS_REGION = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION", "us-east-1")

OPENAI_API_KEY: str | None = None

try:
    secret = get_secret("OpenAI-Keys", AWS_REGION)
    OPENAI_API_KEY = secret.get("OPENAI_API_KEY")
    if OPENAI_API_KEY:
        print("Loaded API key from AWS Secrets Manager")
    else:
        print("Secret found but 'OPENAI_API_KEY' key is missing inside it")
except Exception as e:
    print(f"Secrets Manager unavailable ({e}), falling back to env var")

if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY:
        print("Loaded API key from environment variable")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY not found.\n"
        "  • Locally : add it to your .env file\n"
        "  • On EC2  : pass -e OPENAI_API_KEY=sk-... to docker run, "
        "or attach an IAM role with Secrets Manager access and set "
        "AWS_DEFAULT_REGION in the container environment."
    )


# ─────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────
app = FastAPI(title="AI Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY,
)


class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = Field(default_factory=list)
    system_prompt: str = Field(default="You are a helpful AI assistant.")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "AI Chatbot API is running. POST to /chat to interact."}


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        messages = []

        if req.system_prompt:
            messages.append(SystemMessage(content=req.system_prompt))

        for h in req.history:
            role    = h.get("role", "")
            content = h.get("content", "")
            if not content:
                continue
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

        messages.append(HumanMessage(content=req.message))

        response = await llm.ainvoke(messages)
        return {"reply": response.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Entry point for local run: python backend.py
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend:app", host="0.0.0.0", port=port, reload=False)


    

# python backend.py