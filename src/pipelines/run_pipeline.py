from src.langchain_ext.document_loader import get_openai_api_key
from src.langchain_ext.prompts import get_chat_prompt
from src.langchain_ext.memory import get_memory
from src.langchain_ext.chains import get_chat_chain


def main():
    print("\n🚀 Chatbot Started! Type 'exit' to stop.\n")

    # --- load API key ---
    api_key = get_openai_api_key()

    # --- prompt template ---
    prompt = get_chat_prompt("You are a helpful AI assistant.")

    # --- memory ---
    memory = get_memory()

    # --- full chain (no need to load llm separately, get_chat_chain handles it) ---
    chatbot = get_chat_chain(prompt, memory)
    
    # --- user interaction loop ---
    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        try:
            response = chatbot.predict(input=user_input)
            print(f"AI: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()


# python -m src.pipelines.run_pipeline