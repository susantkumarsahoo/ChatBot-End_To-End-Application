import streamlit as st
from src.pipelines.training_pipeline import initialize_chatbot

def main():
    st.set_page_config(
        page_title="AI Chatbot",
        page_icon="🤖",
        layout="wide"
    )

    # Sidebar
    with st.sidebar:
        st.title("🤖 Chatbot Settings")
        st.divider()
        
        st.subheader("About")
        st.write("This is an AI-powered chatbot built with LangChain and Streamlit.")
        
        st.divider()
        
        # Clear chat button
        #if st.button("🗑️ Clear Chat History", use_container_width=True):
            #st.session_state.messages = []
            #st.session_state.llm = initialize_chatbot()
            #st.rerun()
        
        #st.divider()
        
        # Display message count
        #message_count = len(st.session_state.get('messages', []))
        #st.metric("Total Messages", message_count)

    # Main content
    st.title("💬 AI Chatbot")
    st.caption("Ask me anything!")

    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'chatbot' not in st.session_state:
        with st.spinner("Initializing chatbot..."):
            st.session_state.llms = initialize_chatbot()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if user_input := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.llms.predict(input=user_input)
                    st.markdown(response)
                    
                    # Add assistant message to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                except Exception as e:
                    error_msg = f"⚠️ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

if __name__ == "__main__":
    main()


    # streamlit run main.py