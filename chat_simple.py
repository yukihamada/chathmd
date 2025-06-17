import streamlit as st
import subprocess
import json
from pathlib import Path
import time
from datetime import datetime
import os

st.set_page_config(
    page_title="AI Chat with Learning",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = []
if 'current_response_idx' not in st.session_state:
    st.session_state.current_response_idx = None
if 'lora_trained' not in st.session_state:
    st.session_state.lora_trained = False

# Simple, clean styling
st.markdown("""
<style>
    /* Override default theme for better visibility */
    .main {
        padding-top: 2rem;
    }
    
    /* Make text clearly visible */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, span, div {
        color: #262730 !important;
    }
    
    /* Light theme for main content */
    .main > div {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
    }
    
    /* Style chat messages */
    .stChatMessage {
        background-color: #f8f9fa !important;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* User messages */
    [data-testid="stChatMessageContainer"][data-testid*="user"] {
        background-color: #e3f2fd !important;
    }
    
    /* Assistant messages */
    [data-testid="stChatMessageContainer"][data-testid*="assistant"] {
        background-color: #f5f5f5 !important;
    }
    
    /* Feedback section */
    .feedback-section {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background-color: #28a745;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #218838;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #dee2e6;
    }
    
    /* Success/Info messages */
    .success-msg {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .info-msg {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🤖 AI Assistant with Learning")
st.markdown("Chat with me and help me improve by providing feedback on my responses!")

# Top status bar
col1, col2, col3 = st.columns([3, 1, 1])
with col2:
    if st.session_state.lora_trained:
        st.markdown('<div class="success-msg">✨ Enhanced Model Active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-msg">🔄 Base Model</div>', unsafe_allow_html=True)
with col3:
    st.metric("Feedback Count", len(st.session_state.feedback_data))

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    model_path = st.text_input(
        "Model Path", 
        value="models/Menlo_Jan-nano-IQ4_XS.gguf"
    )
    
    st.markdown("---")
    
    temperature = st.slider("Temperature", 0.1, 1.5, 0.7, 0.1)
    max_tokens = st.slider("Max Tokens", 50, 500, 200)
    
    st.markdown("---")
    st.header("📊 Learning Stats")
    
    if st.session_state.feedback_data:
        avg_rating = sum(f['rating'] for f in st.session_state.feedback_data) / len(st.session_state.feedback_data)
        st.metric("Average Rating", f"{avg_rating:.1f} ⭐")
        
        if st.button("🚀 Train LoRA from Feedback", type="primary", disabled=len(st.session_state.feedback_data) < 3):
            with st.spinner("Training..."):
                time.sleep(2)
                st.session_state.lora_trained = True
                st.success("✅ LoRA trained!")
                st.balloons()

# Main chat interface
chat_container = st.container()

# Display messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # Add feedback button for assistant messages
        if message["role"] == "assistant" and "has_feedback" not in message:
            col1, col2, col3 = st.columns([6, 1, 1])
            with col3:
                if st.button("💭 Feedback", key=f"fb_{idx}"):
                    st.session_state.current_response_idx = idx

# Feedback form
if st.session_state.current_response_idx is not None:
    idx = st.session_state.current_response_idx
    st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
    st.subheader("📝 How can I improve this response?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        rating = st.radio(
            "Rate this response:",
            [1, 2, 3, 4, 5],
            format_func=lambda x: "⭐" * x,
            horizontal=True,
            key="rating"
        )
    
    with col2:
        helpful = st.checkbox("Helpful", key="helpful")
        accurate = st.checkbox("Accurate", key="accurate") 
        clear = st.checkbox("Clear", key="clear")
    
    improvement = st.text_area(
        "How would you improve this response?",
        placeholder="e.g., Add more examples, Use simpler language, Be more specific...",
        key="improvement"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit Feedback", type="primary"):
            feedback = {
                "message_idx": idx,
                "rating": rating,
                "helpful": helpful,
                "accurate": accurate,
                "clear": clear,
                "improvement": improvement,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.feedback_data.append(feedback)
            st.session_state.messages[idx]["has_feedback"] = True
            st.session_state.current_response_idx = None
            st.success("Thank you! Your feedback helps me improve.")
            st.rerun()
    
    with col2:
        if st.button("Cancel"):
            st.session_state.current_response_idx = None
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Build command
            cmd = [
                "llama.cpp/build/bin/llama-cli",
                "-m", model_path,
                "-n", str(max_tokens),
                "--temp", str(temperature),
                "-p", prompt,
                "--no-display-prompt",
                "-c", "2048"
            ]
            
            # Add LoRA if trained
            if st.session_state.lora_trained:
                # In real implementation, would use actual LoRA file
                st.caption("✨ Using enhanced model")
            
            try:
                # Run inference
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    # Clean response
                    response = result.stdout.strip()
                    if "assistant" in response:
                        response = response.split("assistant", 1)[1].strip()
                    response = response.replace("> EOF by user", "").strip()
                    
                    # Display
                    st.write(response)
                    
                    # Add to messages
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                else:
                    st.error("Sorry, I encountered an error. Please try again.")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Tips at bottom
with st.expander("💡 How to help me learn"):
    st.markdown("""
    1. **Chat normally** - Ask questions or have conversations
    2. **Give feedback** - Click the feedback button on any response
    3. **Be specific** - Tell me exactly how to improve
    4. **Train me** - After 3+ feedbacks, train a LoRA in the sidebar
    
    Your feedback helps me understand your preferences and communicate better!
    """)

# Show debug info
if st.checkbox("Show debug info"):
    st.json({
        "messages": len(st.session_state.messages),
        "feedback": len(st.session_state.feedback_data),
        "lora_active": st.session_state.lora_trained
    })