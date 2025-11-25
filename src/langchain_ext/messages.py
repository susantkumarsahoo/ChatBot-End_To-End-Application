from langchain_classic.schema import SystemMessage, HumanMessage

def run_chatbot(user_input: str) -> list:
    """
    Creates a basic chatbot conversation using SystemMessage and HumanMessage.
    
    Args:
        user_input (str): The message from the user.
    
    Returns:
        list: A list of messages representing the conversation.
    """
    # Define the system role (instructions for the chatbot)
    system_msg = SystemMessage(
        content="You are a helpful AI assistant that answers clearly and politely."
    )
    
    # Capture the human/user message
    human_msg = HumanMessage(content=user_input)
    
    # Return the conversation as a list
    conversation = [system_msg, human_msg]
    
    return conversation
