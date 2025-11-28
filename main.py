
import streamlit as st
from src.pipelines.run_pipeline import main

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Chatbot UI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Initialize LLM Pipeline
# -----------------------------
# Load the LLM

llm = main()

# Load the LLM

# -----------------------------
# Initialize Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("Customize your chatbot here.")
    
    if st.button("🆕 New Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()
    
    st.divider()
    
    # Display message count
    message_count = len(st.session_state["messages"])
    st.caption(f"💬 Messages: {message_count}")
    
    # Show pipeline status
    if llm:
        st.success("✅ LLM Pipeline Loaded")
    else:
        st.error("❌ LLM Pipeline Failed")

# -----------------------------
# Main Chat Interface
# -----------------------------
st.title("💬 Chatbot Application")
st.markdown("---")

# -----------------------------
# Display Chat History
# -----------------------------
chat_container = st.container()
with chat_container:
    if len(st.session_state["messages"]) == 0:
        st.info("👋 Start a conversation by typing a message below!")
    else:
        for msg in st.session_state["messages"]:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg["content"])

# -----------------------------
# User Input Box
# -----------------------------
user_input = st.chat_input("Send a message...")

if user_input:
    # Store user message
    st.session_state["messages"].append({
        "role": "user",
        "content": user_input
    })
    
    # Generate bot reply using LLM pipeline
    if llm:
        try:
            # Call your LLM pipeline with user input
            bot_reply = llm(user_input)
            
            # Convert response to string if needed
            if not isinstance(bot_reply, str):
                bot_reply = str(bot_reply)
                
        except Exception as e:
            bot_reply = f"❌ Error: {str(e)}"
    else:
        bot_reply = "⚠️ LLM pipeline is not loaded. Please check your configuration."
    
    # Store bot message
    st.session_state["messages"].append({
        "role": "assistant",
        "content": bot_reply
    })
    
    # Refresh to display new messages
    st.rerun()