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

load_dotenv()

# -----------------------------
# AWS Secrets Manager
# -----------------------------
def get_secret(secret_name: str, region: str = "us-east-1") -> dict:
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region
    )
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise RuntimeError(f"Failed to retrieve secret: {e}")

    return json.loads(response["SecretString"])


# Load API key (AWS first, then .env fallback)
OPENAI_API_KEY = None
try:
    secret = get_secret("OpenAI-Keys", "us-east-1")
    OPENAI_API_KEY = secret.get("OPENAI_API_KEY")
except Exception:
    pass

if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY not found in AWS Secrets Manager or environment variables."
    )


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="AI Chatbot API", version="1.0.0")

# ✅ CORS — required so the Streamlit frontend (different port/domain) can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Tighten this in production, e.g. ["https://your-frontend.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY
)


class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = Field(default_factory=list)
    system_prompt: str = Field(
        default="You are a helpful AI assistant.",
        description="Optional system prompt to customize assistant behavior."
    )


# ✅ Health check endpoint — required by cloud platforms (ECS, App Runner, Railway, etc.)
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

        # Include system prompt if provided
        if req.system_prompt:
            messages.append(SystemMessage(content=req.system_prompt))

        # Rebuild conversation history
        for h in req.history:
            role = h.get("role", "")
            content = h.get("content", "")
            if not content:
                continue
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

        # Append latest user message
        messages.append(HumanMessage(content=req.message))

        response = await llm.ainvoke(messages)

        return {"reply": response.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Entry point for direct execution: python backend.py
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend:app", host="0.0.0.0", port=port, reload=False)


# python backend.py