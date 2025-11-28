from src.langchain_ext.document_loader import get_openai_api_key
from src.langchain_ext.prompts import get_chat_prompt
from src.langchain_ext.memory import get_memory
from src.langchain_ext.chains import get_chat_chain


def initialize_chatbot():
    """Initialize the chatbot with API key, prompt, memory, and chain."""
    api_key = get_openai_api_key()
    prompt = get_chat_prompt("You are a helpful AI assistant.")
    memory = get_memory()
    chatbot = get_chat_chain(prompt, memory)
    return chatbot
