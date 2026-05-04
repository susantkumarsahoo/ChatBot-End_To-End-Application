import streamlit as st
import requests
import os

# -----------------------------
# Dynamic API URL (IMPORTANT)
# -----------------------------
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/chat")

st.set_page_config(page_title="Chatbot", layout="wide")
st.title("🤖 AI Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

# Display chat history
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    try:
        response = requests.post(
            API_URL,
            json={
                "message": user_input,
                "history": st.session_state.history[:-1]
            },
            timeout=30
        )

        if response.status_code == 200:
            reply = response.json()["reply"]
        else:
            detail = response.json().get("detail", response.text)
            reply = f"⚠️ Backend error {response.status_code}: {detail}"

    except requests.exceptions.ConnectionError:
        reply = "❌ Cannot connect to backend."
    except requests.exceptions.Timeout:
        reply = "⏱️ Request timed out."
    except Exception as e:
        reply = f"❌ Error: {str(e)}"

    st.session_state.history.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.write(reply)


# Run: streamlit run frontend_app.py