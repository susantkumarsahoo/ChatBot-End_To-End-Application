from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
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


# Load API key
try:
    secret = get_secret("OpenAI-Keys", "us-east-1")
    OPENAI_API_KEY = secret["OPENAI_API_KEY"]
except Exception:
    # fallback for local dev
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY
)


class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = Field(default_factory=list)


@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        messages = []

        for h in req.history:
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            else:
                messages.append(AIMessage(content=h["content"]))

        messages.append(HumanMessage(content=req.message))

        response = await llm.ainvoke(messages)

        return {"reply": response.content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# python backend.py