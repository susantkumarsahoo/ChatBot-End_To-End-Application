from langchain_openai import ChatOpenAI
from langchain_classic.chains import ConversationChain
from src.langchain_ext.document_loader import get_openai_api_key

def create_conversation_chain(
    model_name: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    max_tokens: int = 500
) -> ConversationChain:
    """
    Creates and returns a ConversationChain using OpenAI's chat model.

    Args:
        model_name (str): The model to use (e.g., "gpt-3.5-turbo", "gpt-4-turbo").
        temperature (float): Controls creativity (0 = factual, 1 = creative).
        max_tokens (int): Maximum response length.

    Returns:
        ConversationChain: A ready-to-use conversation chain.
    """
    chat_model = ChatOpenAI(
        openai_api_key=get_openai_api_key(),
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )

    return ConversationChain(llm=chat_model)
