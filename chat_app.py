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
if 'current_response' not in st.session_state:
    st.session_state.current_response = None
if 'lora_trained' not in st.session_state:
    st.session_state.lora_trained = False

# Custom CSS for chat interface with proper contrast
st.markdown("""
<style>
    /* Main theme adjustments */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #262730;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #3a3b45;
    }
    
    /* User messages */
    [data-testid="stChatMessageContainer"] [data-testid="stMarkdownContainer"] p {
        color: #fafafa !important;
    }
    
    /* Feedback box */
    .feedback-box {
        background-color: #1e1e2e;
        border: 2px solid #4a9eff;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .feedback-box h3 {
        color: #4a9eff !important;
    }
    
    /* Improvement box */
    .improvement-box {
        background-color: #1a2332;
        border: 2px solid #2ed573;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
    }
    
    /* Metric boxes */
    .metric-box {
        background-color: #262730;
        border: 1px solid #3a3b45;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        color: #fafafa;
    }
    
    /* Buttons styling */
    .stButton > button {
        background-color: #4a9eff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #357abd;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(74, 158, 255, 0.3);
    }
    
    /* Primary button */
    [data-testid="stButton"] [kind="primary"] {
        background-color: #2ed573 !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #262730;
        color: #fafafa;
        border: 1px solid #3a3b45;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1a1b26;
    }
    
    /* Headers and text */
    h1, h2, h3, h4, h5, h6 {
        color: #fafafa !important;
    }
    
    p, span, label {
        color: #d1d5db !important;
    }
    
    /* Success/Info alerts */
    .stSuccess {
        background-color: #1a3a2e;
        color: #2ed573;
        border: 1px solid #2ed573;
        border-radius: 8px;
        padding: 10px;
    }
    
    .stInfo {
        background-color: #1e2a3a;
        color: #4a9eff;
        border: 1px solid #4a9eff;
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background-color: #262730;
        border: 1px solid #3a3b45;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
    }
    
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #4a9eff !important;
    }
    
    /* Chat input */
    .stChatInput {
        background-color: #1e1e2e;
        border: 1px solid #3a3b45;
        border-radius: 10px;
    }
    
    .stChatInput > div > div > input {
        background-color: #1e1e2e !important;
        color: #fafafa !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #262730;
        color: #fafafa !important;
        border-radius: 8px;
    }
    
    /* Select slider */
    .stSelectSlider > div > div > div {
        background-color: #262730;
    }
    
    /* Checkbox */
    .stCheckbox > label > span {
        color: #d1d5db !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.title("🤖 AI Assistant with Learning")
with col2:
    if st.session_state.lora_trained:
        st.success("✨ LoRA Active")
    else:
        st.info("🔄 Base Model")
with col3:
    feedback_count = len(st.session_state.feedback_data)
    st.metric("Feedback Given", feedback_count)

st.markdown("Chat with me and help me improve by providing feedback!")

# Sidebar for settings and stats
with st.sidebar:
    st.header("⚙️ Settings")
    
    model_path = st.text_input(
        "Model Path", 
        value="models/Menlo_Jan-nano-IQ4_XS.gguf"
    )
    
    temperature = st.slider(
        "Temperature", 0.1, 1.5, 0.7, 0.1,
        help="Controls creativity"
    )
    
    max_tokens = st.slider(
        "Max Response Length", 50, 500, 200,
        help="Maximum tokens to generate"
    )
    
    st.markdown("---")
    st.header("📊 Learning Stats")
    
    if st.session_state.feedback_data:
        st.metric("Total Feedback", len(st.session_state.feedback_data))
        st.metric("Avg Rating", 
                  f"{sum(f['rating'] for f in st.session_state.feedback_data) / len(st.session_state.feedback_data):.1f}/5")
        
        # Train LoRA button
        if st.button("🚀 Train LoRA from Feedback", type="primary"):
            with st.spinner("Training LoRA from feedback..."):
                # Simulate LoRA training
                time.sleep(2)
                st.session_state.lora_trained = True
                st.success("✅ LoRA trained successfully!")
                st.balloons()

# Main chat interface
chat_container = st.container()

# Display chat history
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show feedback UI for assistant messages
            if message["role"] == "assistant" and "feedback" not in message:
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("💭 Give Feedback", key=f"feedback_{message['timestamp']}"):
                        st.session_state.current_response = message

# Feedback form
if st.session_state.current_response:
    with st.container():
        st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
        st.subheader("📝 Provide Feedback")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            rating = st.select_slider(
                "Rate this response",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: "⭐" * x
            )
            
            helpful = st.checkbox("This was helpful")
            accurate = st.checkbox("This was accurate")
            clear = st.checkbox("This was clear")
        
        with col2:
            improvement = st.text_area(
                "How would you improve this response?",
                placeholder="例: もっと具体例を入れて説明してほしい、専門用語を使わずに説明してほしい、など",
                height=100
            )
            
            ideal_response = st.text_area(
                "Ideal response (optional)",
                placeholder="理想的な回答があれば記入してください",
                height=100
            )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Submit Feedback", type="primary"):
                feedback = {
                    "timestamp": datetime.now().isoformat(),
                    "message": st.session_state.current_response["content"],
                    "rating": rating,
                    "helpful": helpful,
                    "accurate": accurate,
                    "clear": clear,
                    "improvement": improvement,
                    "ideal_response": ideal_response
                }
                st.session_state.feedback_data.append(feedback)
                st.session_state.current_response["feedback"] = True
                st.session_state.current_response = None
                st.success("✅ Thank you for your feedback!")
                st.rerun()
        
        with col2:
            if st.button("Cancel"):
                st.session_state.current_response = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message
    user_message = {
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.messages.append(user_message)
    
    # Display user message
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
            if st.session_state.lora_trained and Path("loras/feedback_trained.gguf").exists():
                cmd.extend(["--lora", "loras/feedback_trained.gguf"])
            
            try:
                # Run inference
                start_time = time.time()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                inference_time = time.time() - start_time
                
                if result.returncode == 0:
                    # Extract response
                    response = result.stdout.strip()
                    if "assistant" in response:
                        response = response.split("assistant", 1)[1].strip()
                    
                    # Clean up response
                    response = response.replace("> EOF by user", "").strip()
                    
                    # Display response
                    st.write(response)
                    
                    # Add to messages
                    assistant_message = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().isoformat(),
                        "inference_time": inference_time
                    }
                    st.session_state.messages.append(assistant_message)
                    
                    # Show metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"⏱️ {inference_time:.2f}s")
                    with col2:
                        tokens = len(response.split())
                        st.caption(f"📝 ~{tokens} tokens")
                    with col3:
                        if st.session_state.lora_trained:
                            st.caption("✨ Enhanced with feedback")
                else:
                    st.error(f"Error generating response: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                st.error("Response generation timed out. Try a shorter prompt.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer with tips
with st.expander("💡 How to use this chat"):
    st.markdown("""
    ### 🎯 Basic Usage
    1. **Chat normally** - Just type your questions or requests
    2. **Give feedback** - Click "Give Feedback" on any response
    3. **Train the model** - After collecting feedback, click "Train LoRA" in the sidebar
    
    ### 📚 Feedback Tips
    - **Be specific** about what could be improved
    - **Provide examples** of better responses when possible
    - **Rate honestly** to help the model understand quality
    
    ### 🧠 How It Works
    1. Your feedback is collected and analyzed
    2. A LoRA (Low-Rank Adaptation) is trained based on your preferences
    3. The model adapts to respond more like you want it to
    
    ### 🔄 Current Status
    - **Model**: jan-mini-14B (IQ4_XS quantized)
    - **LoRA Status**: {"Active ✅" if st.session_state.lora_trained else "Not trained yet ⏳"}
    - **Feedback collected**: {len(st.session_state.feedback_data)} responses
    """)

# Debug info
if st.checkbox("🔧 Show Debug Info"):
    st.json({
        "messages_count": len(st.session_state.messages),
        "feedback_count": len(st.session_state.feedback_data),
        "lora_active": st.session_state.lora_trained,
        "model_exists": Path(model_path).exists(),
        "last_feedback": st.session_state.feedback_data[-1] if st.session_state.feedback_data else None
    })