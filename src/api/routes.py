from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn

from src.langchain_ext.document_loader import get_openai_api_key
from src.langchain_ext.prompts import get_chat_prompt
from src.langchain_ext.memory import get_memory
from src.langchain_ext.chains import get_chat_chain


# Initialize FastAPI app
app = FastAPI(
    title="AI Chatbot API",
    description="Backend API for conversational AI chatbot using LangChain",
    version="1.0.0"
)

# Add CORS middleware - IMPORTANT for Streamlit connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (including Streamlit)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store chatbots for different sessions
chatbot_sessions: Dict[str, dict] = {}


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    model_name: Optional[str] = "gpt-4o-mini"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500


class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str


class InitializeRequest(BaseModel):
    session_id: str = "default"
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 500


class ResetRequest(BaseModel):
    session_id: str = "default"


class HealthResponse(BaseModel):
    status: str
    message: str
    active_sessions: int


def create_chatbot_session(session_id: str, model_name: str, temperature: float, max_tokens: int):
    """Create a new chatbot session"""
    try:
        # Load API key
        api_key = get_openai_api_key()
        
        # Create prompt template
        prompt = get_chat_prompt("You are a helpful AI assistant that provides clear and concise answers.")
        
        # Initialize memory
        memory = get_memory()
        
        # Create chatbot chain with custom parameters
        from src.langchain_ext.chains import get_chat_chain
        chatbot = get_chat_chain(
            prompt=prompt,
            memory=memory,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Store session
        chatbot_sessions[session_id] = {
            "chatbot": chatbot,
            "memory": memory,
            "config": {
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        }
        
        return True
    except Exception as e:
        print(f"Error creating session: {e}")
        return False


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return {
        "status": "success",
        "message": "AI Chatbot API is running! Use /docs for API documentation.",
        "active_sessions": len(chatbot_sessions)
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Backend is ready to receive requests",
        "active_sessions": len(chatbot_sessions)
    }


@app.post("/initialize")
async def initialize_chatbot(request: InitializeRequest):
    """
    Initialize a new chatbot session
    """
    try:
        success = create_chatbot_session(
            session_id=request.session_id,
            model_name=request.model_name,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        if success:
            return {
                "status": "success",
                "message": "Chatbot session initialized successfully!",
                "session_id": request.session_id
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize chatbot session"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing chatbot: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint to send messages and get responses
    """
    # Check if session exists, if not create it
    if request.session_id not in chatbot_sessions:
        success = create_chatbot_session(
            session_id=request.session_id,
            model_name=request.model_name,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        if not success:
            raise HTTPException(
                status_code=503,
                detail="Failed to create chatbot session"
            )
    
    if not request.message or request.message.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )
    
    try:
        # Get chatbot for this session
        session = chatbot_sessions[request.session_id]
        chatbot = session["chatbot"]
        
        # Get response from chatbot
        response = chatbot.predict(input=request.message)
        
        return {
            "response": response,
            "session_id": request.session_id,
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing message: {str(e)}"
        )


@app.post("/reset")
async def reset_conversation(request: ResetRequest):
    """Reset conversation memory for a session"""
    try:
        if request.session_id in chatbot_sessions:
            # Get existing config
            config = chatbot_sessions[request.session_id]["config"]
            
            # Recreate session with same config
            success = create_chatbot_session(
                session_id=request.session_id,
                model_name=config["model_name"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )
            
            if success:
                return {
                    "status": "success",
                    "message": "Conversation reset successfully!",
                    "session_id": request.session_id
                }
        else:
            return {
                "status": "success",
                "message": "No active session to reset",
                "session_id": request.session_id
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting conversation: {str(e)}"
        )


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific session"""
    if session_id in chatbot_sessions:
        del chatbot_sessions[session_id]
        return {
            "status": "success",
            "message": f"Session {session_id} deleted successfully"
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )


if __name__ == "__main__":
    print("🚀 Starting FastAPI Backend Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API Documentation at: http://localhost:8000/docs")
    print("=" * 60)
    import uvicorn
    uvicorn.run(
        "src.api.routes:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )


# python -m src.api.routes