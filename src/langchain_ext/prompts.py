from langchain_classic.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.langchain_ext.messages import run_chatbot

def build_chat_prompt(system_message: str) -> ChatPromptTemplate:
    """
    Build and return a ChatPromptTemplate with system message,
    history placeholder, and user input.

    Args:
        system_message (str): The system message to include.

    Returns:
        ChatPromptTemplate: Configured prompt template.
    """
    return ChatPromptTemplate.from_messages(run_chatbot)
