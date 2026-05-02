import streamlit as st
import requests

API_URL = "http://localhost:8000/chat"

st.title("🤖 Simple Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

# Display chat history
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Call backend
    try:
        response = requests.post(API_URL, json={
            "message": user_input,
            "history": st.session_state.history[:-1]
        }, timeout=30)

        if response.status_code == 200:
            reply = response.json()["reply"]
        else:
            # ✅ Show backend error detail clearly
            detail = response.json().get("detail", response.text)
            reply = f"⚠️ Backend error {response.status_code}: {detail}"

    except requests.exceptions.ConnectionError:
        reply = "❌ Cannot connect to backend. Make sure uvicorn is running."
    except requests.exceptions.Timeout:
        reply = "⏱️ Request timed out. Backend is taking too long to respond."
    except requests.exceptions.JSONDecodeError:
        reply = f"❌ Backend returned invalid response: {response.text}"
    except Exception as e:
        reply = f"❌ Unexpected error: {str(e)}"

    # Show assistant reply
    st.session_state.history.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)


# Run: streamlit run frontend_app.py