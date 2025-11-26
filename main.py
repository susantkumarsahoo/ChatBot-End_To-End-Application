import streamlit as st
from datetime import datetime
import requests
import uuid


# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API URL - Change this if your FastAPI runs on different host/port
API_URL = "http://localhost:8000"

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stTextInput > div > div > input {
        background-color: white;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    .bot-message {
        background-color: #f1f8e9;
        border-left: 5px solid #4caf50;
    }
    .message-header {
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    .message-content {
        font-size: 1rem;
        line-height: 1.6;
    }
    .timestamp {
        font-size: 0.75rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .status-connected {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .status-disconnected {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "backend_status" not in st.session_state:
    st.session_state.backend_status = "unknown"

if "initialized" not in st.session_state:
    st.session_state.initialized = False


def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            st.session_state.backend_status = "connected"
            return True
    except requests.exceptions.RequestException:
        st.session_state.backend_status = "disconnected"
        return False
    return False


def initialize_chatbot(model_name, temperature, max_tokens):
    """Initialize chatbot session on backend"""
    try:
        response = requests.post(
            f"{API_URL}/initialize",
            json={
                "session_id": st.session_state.session_id,
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=30
        )
        
        if response.status_code == 200:
            st.session_state.initialized = True
            return True, "Chatbot initialized successfully!"
        else:
            return False, f"Error: {response.json().get('detail', 'Unknown error')}"
    
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"


def send_message(message, model_name, temperature, max_tokens):
    """Send message to backend and get response"""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "message": message,
                "session_id": st.session_state.session_id,
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, data["response"]
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            return False, f"Error: {error_detail}"
    
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"


def reset_conversation():
    """Reset the conversation on backend"""
    try:
        response = requests.post(
            f"{API_URL}/reset",
            json={"session_id": st.session_state.session_id},
            timeout=10
        )
        
        if response.status_code == 200:
            st.session_state.messages = []
            return True, "Conversation reset successfully!"
        else:
            return False, "Failed to reset conversation"
    
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"


def display_message(role, content, timestamp):
    """Display a chat message with styling"""
    if role == "user":
        message_class = "user-message"
        icon = "👤"
        header = "You"
    else:
        message_class = "bot-message"
        icon = "🤖"
        header = "AI Assistant"
    
    st.markdown(f"""
        <div class="chat-message {message_class}">
            <div class="message-header">{icon} {header}</div>
            <div class="message-content">{content}</div>
            <div class="timestamp">{timestamp}</div>
        </div>
    """, unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("---")
    
    # Backend status
    st.subheader("🔌 Backend Status")
    
    if st.button("🔄 Check Connection", use_container_width=True):
        check_backend_health()
    
    if st.session_state.backend_status == "connected":
        st.markdown("""
            <div class="status-box status-connected">
                <strong>✅ Connected</strong><br>
                Backend is running
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="status-box status-disconnected">
                <strong>❌ Disconnected</strong><br>
                Please start FastAPI backend
            </div>
        """, unsafe_allow_html=True)
        st.code("python fastapi_app.py", language="bash")
    
    st.markdown("---")
    
    # Model settings
    st.subheader("🔧 Model Configuration")
    model_name = st.selectbox(
        "Select Model",
        ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4"],
        index=0
    )
    
    temperature = st.slider(
        "Temperature (Creativity)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more creative"
    )
    
    max_tokens = st.slider(
        "Max Tokens",
        min_value=100,
        max_value=2000,
        value=500,
        step=100,
        help="Maximum length of response"
    )
    
    st.markdown("---")
    
    # Initialize button
    if st.button("🚀 Initialize Chatbot", use_container_width=True):
        with st.spinner("Initializing..."):
            check_backend_health()
            if st.session_state.backend_status == "connected":
                success, message = initialize_chatbot(model_name, temperature, max_tokens)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Backend is not running! Please start FastAPI first.")
    
    # Reset button
    if st.button("🔄 Reset Conversation", use_container_width=True):
        if st.session_state.backend_status == "connected":
            success, message = reset_conversation()
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.error("Backend is not running!")
    
    st.markdown("---")
    
    # Information
    st.subheader("ℹ️ How to Use")
    st.info("""
    **Steps:**
    1. Start FastAPI backend
    2. Check connection (green = good)
    3. Click 'Initialize Chatbot'
    4. Start chatting!
    """)
    
    # Stats
    st.markdown("---")
    st.subheader("📊 Statistics")
    st.metric("Your Messages", len([m for m in st.session_state.messages if m["role"] == "user"]))
    st.metric("Total Messages", len(st.session_state.messages))
    st.caption(f"Session ID: {st.session_state.session_id[:8]}...")


# Main content
st.title("🤖 AI Chatbot")
st.markdown("### Chat with your intelligent AI assistant")

# Auto-check backend on load
if st.session_state.backend_status == "unknown":
    check_backend_health()

st.markdown("---")

# Check if backend is running
if st.session_state.backend_status != "connected":
    st.error("⚠️ Backend is not running! Please start the FastAPI server first.")
    st.code("python fastapi_app.py", language="bash")
    st.info("After starting the backend, click 'Check Connection' in the sidebar.")
    st.stop()

# Check if chatbot is initialized
if not st.session_state.initialized:
    st.warning("⚠️ Please initialize the chatbot using the sidebar button first!")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Quick Initialize", use_container_width=True):
            with st.spinner("Initializing chatbot..."):
                success, message = initialize_chatbot(model_name, temperature, max_tokens)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
else:
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        if len(st.session_state.messages) == 0:
            st.info("👋 Start a conversation by typing a message below!")
        else:
            for message in st.session_state.messages:
                display_message(
                    message["role"],
                    message["content"],
                    message["timestamp"]
                )
    
    # Chat input
    st.markdown("---")
    
    # Input area
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Your message:",
            value="",
            placeholder="Type your message here...",
            label_visibility="collapsed",
            key="message_input"
        )
    
    with col2:
        send_button = st.button("📤 Send", use_container_width=True, type="primary")
    
    # Process user input
    if send_button and user_input:
        if user_input.strip():
            # Get current timestamp
            timestamp = datetime.now().strftime("%I:%M %p")
            
            # Add user message to history
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": timestamp
            })
            
            # Get bot response
            with st.spinner("🤔 AI is thinking..."):
                success, response = send_message(user_input, model_name, temperature, max_tokens)
            
            if success:
                # Add bot response to history
                bot_timestamp = datetime.now().strftime("%I:%M %p")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": bot_timestamp
                })
                
                # Rerun to update the display
                st.rerun()
            else:
                st.error(f"❌ {response}")
    
    # Alternative: Press Enter to send
    if user_input and not send_button:
        st.info("💡 Tip: Click the 'Send' button to send your message")


# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🔗 <strong>Connected to FastAPI Backend</strong></p>
        <p>Built with ❤️ using Streamlit, FastAPI, and LangChain</p>
    </div>
""", unsafe_allow_html=True)


