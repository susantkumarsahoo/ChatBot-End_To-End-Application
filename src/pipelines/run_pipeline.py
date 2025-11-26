# pipeline.py
from src.langchain_ext.document_loader import get_openai_api_key
from src.langchain_ext.prompts import get_chat_prompt
from src.langchain_ext.memory import get_memory
from src.langchain_ext.llms_chat_model import get_chat_model
from src.langchain_ext.chains import get_chat_chain
from langchain_classic.chains import ConversationChain


def main():
    print("\n🚀 Chatbot Started! Type 'exit' to stop.\n")

    # --- load API key ---
    api_key = get_openai_api_key()

    # --- prompt template ---
    prompt = get_chat_prompt("You are a helpful AI assistant.")

    # --- memory ---
    memory = get_memory()

    # --- load LLM model ---
    llm = get_chat_model(api_key)

    # --- full chain ---
    chain = get_chat_chain(prompt, memory, llm)
    
    chatbot = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=prompt,
    verbose=True
)


    # --- user interaction loop ---
    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        response = chatbot.invoke({"input": user_input})
        print("AI:", response["response"])

if __name__ == "__main__":
    main()

# python src/pipelines/run_pipeline.py
# python -m src.pipelines.run_pipeline