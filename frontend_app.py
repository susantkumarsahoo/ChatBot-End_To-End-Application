import streamlit as st
import requests

API_URL = "http://localhost:8000/chat"

st.title("🤖 Simple Chatbot")

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    response = requests.post(API_URL, json={
        "message": user_input,
        "history": st.session_state.history[:-1]
    })
    reply = response.json()["reply"]

    st.session_state.history.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)