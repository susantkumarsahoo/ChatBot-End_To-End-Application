from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
 
load_dotenv()
 
app = FastAPI()
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
 
class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
 
@app.post("/chat")
def chat(req: ChatRequest):
    messages = []
    for h in req.history:
        if h["role"] == "user":
            messages.append(HumanMessage(content=h["content"]))
        else:
            messages.append(AIMessage(content=h["content"]))
    messages.append(HumanMessage(content=req.message))
 
    response = llm.invoke(messages)
    return {"reply": response.content}