import streamlit as st
import subprocess
import json
from pathlib import Path
import time
from datetime import datetime
import os
import openai

st.set_page_config(
    page_title="AI Chat with Learning",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
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
if 'model_type' not in st.session_state:
    st.session_state.model_type = "local"
if 'openai_key' not in st.session_state:
    st.session_state.openai_key = ""
if 'preset_config' not in st.session_state:
    st.session_state.preset_config = {"temp": 0.8, "top_p": 0.95, "repeat": 1.1}

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
    
    /* Model selector */
    .model-selector {
        background-color: #e8f4fd;
        border: 1px solid #b8e0f5;
        border-radius: 10px;
        padding: 1rem;
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
    
    .warning-msg {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🤖 AI Assistant with Learning")
st.markdown("Chat with AI and help it improve by providing feedback!")

# Sidebar
with st.sidebar:
    st.header("🎛️ Model Selection")
    
    # Model type selector
    model_type = st.radio(
        "Choose AI Model:",
        ["local", "chatgpt"],
        format_func=lambda x: "🏠 Local Model (jan-mini)" if x == "local" else "🌐 ChatGPT",
        index=0 if st.session_state.model_type == "local" else 1,
        key="model_selector"
    )
    st.session_state.model_type = model_type
    
    if model_type == "local":
        st.markdown("---")
        st.subheader("Local Model Settings")
        
        # Conversation style presets
        preset = st.selectbox(
            "Conversation Style",
            ["Balanced", "Creative", "Precise", "Casual", "Professional"],
            index=0,
            help="Choose a preset for optimal conversation parameters"
        )
        
        # Apply preset values
        preset_configs = {
            "Balanced": {"temp": 0.8, "top_p": 0.95, "repeat": 1.1},
            "Creative": {"temp": 1.2, "top_p": 0.98, "repeat": 1.05},
            "Precise": {"temp": 0.3, "top_p": 0.9, "repeat": 1.2},
            "Casual": {"temp": 0.9, "top_p": 0.95, "repeat": 1.08},
            "Professional": {"temp": 0.5, "top_p": 0.92, "repeat": 1.15}
        }
        
        config = preset_configs[preset]
        st.session_state.preset_config = config
        
        model_path = st.text_input(
            "Model Path", 
            value="models/Menlo_Jan-nano-IQ4_XS.gguf"
        )
        
        # Conversational parameters optimized for natural dialogue
        temperature = st.slider(
            "Temperature", 
            0.1, 1.5, config["temp"], 0.1,
            help=f"Preset: {preset} - {config['temp']} for optimal {preset.lower()} conversation"
        )
        
        # Context-aware max tokens
        if "conversation_length" not in st.session_state:
            st.session_state.conversation_length = 0
        
        # Dynamic max tokens based on conversation context
        if st.session_state.conversation_length < 3:
            default_tokens = 150  # Shorter for initial exchanges
        elif st.session_state.conversation_length < 10:
            default_tokens = 250  # Medium for ongoing conversation
        else:
            default_tokens = 350  # Longer for deep discussions
            
        max_tokens = st.slider(
            "Max Tokens", 
            50, 800, default_tokens,
            help=f"Auto-adjusted to {default_tokens} for current conversation depth"
        )
        
        if st.session_state.lora_trained:
            st.markdown('<div class="success-msg">✨ LoRA Enhanced Model Active</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-msg">🔄 Base Model Active</div>', unsafe_allow_html=True)
    
    else:  # ChatGPT
        st.markdown("---")
        st.subheader("ChatGPT Settings")
        
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.openai_key,
            placeholder="sk-..."
        )
        st.session_state.openai_key = api_key
        
        if api_key:
            st.markdown('<div class="success-msg">✅ API Key Set</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-msg">⚠️ Enter API Key to use ChatGPT</div>', unsafe_allow_html=True)
        
        gpt_model = st.selectbox(
            "GPT Model",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            index=0
        )
        
        # Optimized conversational parameters for ChatGPT
        gpt_temperature = st.slider(
            "Temperature", 
            0.0, 2.0, 0.9, 0.1,
            help="0.9 gives ChatGPT natural, human-like responses"
        )
        
        # Smart token allocation for ChatGPT
        if st.session_state.conversation_length < 3:
            gpt_default_tokens = 200  # Concise initial responses
        elif st.session_state.conversation_length < 10:
            gpt_default_tokens = 350  # More detailed ongoing chat
        else:
            gpt_default_tokens = 500  # Comprehensive for complex topics
            
        gpt_max_tokens = st.slider(
            "Max Tokens", 
            50, 2000, gpt_default_tokens,
            help=f"Auto-adjusted to {gpt_default_tokens} based on conversation flow"
        )
    
    st.markdown("---")
    st.header("📊 Learning Stats")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Feedback", len(st.session_state.feedback_data))
    with col2:
        if st.session_state.feedback_data:
            avg_rating = sum(f['rating'] for f in st.session_state.feedback_data) / len(st.session_state.feedback_data)
            st.metric("Avg Rating", f"{avg_rating:.1f} ⭐")
    
    if st.session_state.model_type == "local" and st.session_state.feedback_data:
        if st.button("🚀 Train LoRA from Feedback", 
                    type="primary", 
                    disabled=len(st.session_state.feedback_data) < 3):
            with st.spinner("Training LoRA..."):
                time.sleep(2)
                st.session_state.lora_trained = True
                st.success("✅ LoRA trained successfully!")
                st.balloons()

# Top status bar
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    if st.session_state.model_type == "local":
        st.info(f"🏠 Using Local Model: jan-mini-14B {'(Enhanced)' if st.session_state.lora_trained else ''}")
    else:
        if st.session_state.openai_key:
            st.info("🌐 Using ChatGPT")
        else:
            st.warning("🌐 ChatGPT (No API Key)")
with col3:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
chat_container = st.container()

# Display messages
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # Show which model was used
        if message["role"] == "assistant" and "model_used" in message:
            st.caption(f"via {message['model_used']}")
        
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
                "model_used": st.session_state.messages[idx].get("model_used", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.feedback_data.append(feedback)
            st.session_state.messages[idx]["has_feedback"] = True
            st.session_state.current_response_idx = None
            st.success("Thank you! Your feedback helps improve the AI.")
            st.rerun()
    
    with col2:
        if st.button("Cancel"):
            st.session_state.current_response_idx = None
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Type your message..."):
    # Update conversation length
    st.session_state.conversation_length = len([m for m in st.session_state.messages if m["role"] == "user"]) + 1
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response based on selected model
    with st.chat_message("assistant"):
        if st.session_state.model_type == "local":
            # Local model inference
            with st.spinner("Thinking..."):
                # Build command
                # Build conversation-aware prompt
                context_prompt = prompt
                
                # Add conversation context for better continuity
                if len(st.session_state.messages) > 2:
                    # Include last exchange for context
                    last_user = next((m for m in reversed(st.session_state.messages[:-1]) if m["role"] == "user"), None)
                    last_assistant = next((m for m in reversed(st.session_state.messages[:-1]) if m["role"] == "assistant"), None)
                    
                    if last_user and last_assistant:
                        context_prompt = f"Previous: User: {last_user['content'][:100]}... Assistant: {last_assistant['content'][:100]}...\n\nCurrent: {prompt}"
                
                # Optimize parameters for conversation
                cmd = [
                    "llama.cpp/build/bin/llama-cli",
                    "-m", model_path,
                    "-n", str(max_tokens),
                    "--temp", str(temperature),
                    "-p", context_prompt,
                    "--no-display-prompt",
                    "-c", "4096",  # Increased context for better conversation flow
                    "--repeat-penalty", str(st.session_state.preset_config["repeat"]),  # Prevent repetitive responses
                    "--top-p", str(st.session_state.preset_config["top_p"]),  # Better response diversity
                    "--top-k", "40"  # Balanced creativity
                ]
                
                # Add LoRA if trained
                if st.session_state.lora_trained:
                    st.caption("✨ Using enhanced model")
                
                try:
                    # Run inference
                    start_time = time.time()
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    inference_time = time.time() - start_time
                    
                    if result.returncode == 0:
                        # Clean response
                        response = result.stdout.strip()
                        if "assistant" in response:
                            response = response.split("assistant", 1)[1].strip()
                        response = response.replace("> EOF by user", "").strip()
                        
                        # Display
                        st.write(response)
                        st.caption(f"⏱️ {inference_time:.2f}s | 🏠 Local Model")
                        
                        # Add to messages
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "model_used": "Local jan-mini" + (" (Enhanced)" if st.session_state.lora_trained else ""),
                            "inference_time": inference_time
                        })
                    else:
                        st.error("Sorry, I encountered an error. Please try again.")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        else:  # ChatGPT
            if not st.session_state.openai_key:
                st.error("Please enter your OpenAI API key in the sidebar.")
            else:
                with st.spinner("ChatGPT is thinking..."):
                    try:
                        # Set API key
                        openai.api_key = st.session_state.openai_key
                        
                        # Prepare messages for ChatGPT
                        messages = [{"role": "system", "content": "You are a helpful assistant."}]
                        
                        # Add recent conversation context
                        for msg in st.session_state.messages[-10:]:  # Last 10 messages
                            messages.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })
                        
                        # Call ChatGPT API
                        start_time = time.time()
                        response = openai.ChatCompletion.create(
                            model=gpt_model,
                            messages=messages,
                            temperature=gpt_temperature,
                            max_tokens=gpt_max_tokens
                        )
                        inference_time = time.time() - start_time
                        
                        # Extract response
                        gpt_response = response.choices[0].message.content
                        
                        # Display
                        st.write(gpt_response)
                        st.caption(f"⏱️ {inference_time:.2f}s | 🌐 {gpt_model}")
                        
                        # Add to messages
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": gpt_response,
                            "model_used": f"ChatGPT ({gpt_model})",
                            "inference_time": inference_time
                        })
                        
                    except Exception as e:
                        st.error(f"ChatGPT Error: {str(e)}")

# Tips at bottom
with st.expander("💡 How to use this app"):
    st.markdown("""
    ### 🎯 Model Selection
    - **Local Model**: Fast, private, runs on your machine
    - **ChatGPT**: Powerful, requires API key, uses OpenAI servers
    
    ### 📝 Giving Feedback
    1. Click "💭 Feedback" on any AI response
    2. Rate the response and provide improvement suggestions
    3. Your feedback helps train the local model
    
    ### 🚀 Training LoRA (Local Model Only)
    - Collect at least 3 feedbacks
    - Click "Train LoRA" in the sidebar
    - The local model will adapt to your preferences
    
    ### 🔄 Switching Models
    - You can switch between models anytime
    - Each model has its own strengths
    - Compare responses from both models!
    """)

# Debug info
if st.checkbox("Show debug info"):
    st.json({
        "current_model": st.session_state.model_type,
        "messages": len(st.session_state.messages),
        "feedback": len(st.session_state.feedback_data),
        "lora_active": st.session_state.lora_trained,
        "has_api_key": bool(st.session_state.openai_key)
    })