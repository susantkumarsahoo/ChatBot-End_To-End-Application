import streamlit as st
import requests
import os

# ─────────────────────────────────────────
# API URL configuration
# ─────────────────────────────────────────
# In production set API_URL env var to your deployed backend URL.
# e.g. http://<EC2-public-ip>:8000/chat
# When running in the same container, the default below is correct.
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/chat")

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 AI Chatbot")
st.caption(f"Connected to: `{API_URL}`")

# Session state initialisation
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar: optional system prompt
with st.sidebar:
    st.header("⚙️ Settings")
    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful AI assistant.",
        height=120,
        help="Customise how the assistant behaves.",
    )
    if st.button("🗑️ Clear Chat"):
        st.session_state.history = []
        st.rerun()

# Display existing chat history
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    API_URL,
                    json={
                        "message": user_input,
                        # Send history excluding the message just appended above
                        "history": st.session_state.history[:-1],
                        "system_prompt": system_prompt,
                    },
                    timeout=60,
                )

                if response.status_code == 200:
                    reply = response.json()["reply"]
                else:
                    try:
                        detail = response.json().get("detail", response.text)
                    except Exception:
                        detail = response.text
                    reply = f"⚠️ Backend error {response.status_code}: {detail}"

            except requests.exceptions.ConnectionError:
                reply = (
                    "❌ Cannot connect to the backend. "
                    f"Make sure `API_URL` points to your deployed backend. "
                    f"Current value: `{API_URL}`"
                )
            except requests.exceptions.Timeout:
                reply = "⏱️ Request timed out. The backend may be cold-starting — please try again."
            except Exception as e:
                reply = f"❌ Unexpected error: {str(e)}"

        st.write(reply)

    st.session_state.history.append({"role": "assistant", "content": reply})




# Run: streamlit run frontend_app.py