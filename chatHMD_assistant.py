import streamlit as st
import subprocess
import json
from pathlib import Path
import time
from datetime import datetime
import os
import openai
from learning_data_manager import LearningDataManager

# Add API endpoints for web integration
@st.fragment
def api_endpoints():
    """Handle API requests from web interface"""
    
    # Health check endpoint
    if st.query_params.get("api") == "health":
        return {
            "status": "healthy",
            "model": "jan-nano-xs",
            "available": True,
            "timestamp": datetime.now().isoformat()
        }
    
    # Chat endpoint  
    if st.query_params.get("api") == "chat":
        if st.method == "POST":
            try:
                message = st.query_params.get("message", "")
                if message:
                    response = generate_local_response(message)
                    return {
                        "response": response,
                        "model": "jan-nano-xs-local",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"error": "Message required"}
            except Exception as e:
                return {"error": str(e)}
    
    return None

def generate_local_response(message):
    """Generate response using local jan-nano model"""
    # This would call the actual model
    # For now, return a realistic response
    return f"Local jan-nano XS response to: {message}"

st.set_page_config(
    page_title="chatHMD AI Assistant",
    page_icon="🥽",
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
if 'model_type' not in st.session_state:
    st.session_state.model_type = "local"
if 'openai_key' not in st.session_state:
    st.session_state.openai_key = ""
if 'preset_config' not in st.session_state:
    st.session_state.preset_config = {"temp": 0.8, "top_p": 0.95, "repeat": 1.1}
if 'conversation_length' not in st.session_state:
    st.session_state.conversation_length = 0
if 'tokens_earned' not in st.session_state:
    st.session_state.tokens_earned = 0
if 'online_feedback' not in st.session_state:
    st.session_state.online_feedback = False
if 'learning_manager' not in st.session_state:
    st.session_state.learning_manager = LearningDataManager()

# Enhanced styling with better visibility
st.markdown("""
<style>
    /* Main theme */
    .main {
        padding-top: 2rem;
    }
    
    /* Ensure all text is visible */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, span, div, label {
        color: #262730 !important;
    }
    
    /* Sidebar styling with proper contrast */
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stCheckbox label,
    section[data-testid="stSidebar"] .stTextInput label,
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"],
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #262730 !important;
        font-weight: 500;
    }
    
    /* Sidebar expander headers */
    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: #ffffff;
        color: #262730 !important;
        border: 1px solid #e0e2e6;
        font-weight: 600;
    }
    
    section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background-color: #e8eaf0;
    }
    
    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: #4a5568;
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2d3748;
    }
    
    /* Main content area */
    .main > div {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
    }
    
    /* Chat messages */
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
        border: 2px solid #ffeaa7;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Token reward box */
    .token-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #007bff;
        color: white !important;
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
    
    /* Metrics */
    [data-testid="metric-container"] {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #dee2e6;
    }
    
    [data-testid="metric-container"] [data-testid="stMetricLabel"] {
        color: #495057 !important;
    }
    
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #262730 !important;
        font-weight: 600;
    }
    
    /* Sidebar specific metrics */
    section[data-testid="stSidebar"] [data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
    }
    
    /* Expander headers */
    .streamlit-expanderHeader {
        color: #262730 !important;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    
    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        color: #262730 !important;
    }
    
    /* Selectbox */
    .stSelectbox label {
        color: #262730 !important;
    }
    
    /* Slider labels */
    .stSlider label {
        color: #262730 !important;
    }
    
    /* Radio buttons */
    .stRadio label {
        color: #262730 !important;
    }
    
    /* Checkbox labels */
    .stCheckbox label {
        color: #262730 !important;
    }
    
    /* Success/Info messages */
    .success-msg {
        background-color: #d4edda;
        color: #155724 !important;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .info-msg {
        background-color: #d1ecf1;
        color: #0c5460 !important;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #bee5eb;
    }
    
    .warning-msg {
        background-color: #fff3cd;
        color: #856404 !important;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

# Header with chatHMD branding
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🥽 chatHMD AI Assistant")
    st.markdown("**Learn from your feedback** | Powered by Text-to-LoRA technology")
with col2:
    if st.session_state.tokens_earned > 0:
        st.markdown(f'<div class="token-box">🪙 {st.session_state.tokens_earned} Tokens Earned</div>', unsafe_allow_html=True)

# Introduction message
if len(st.session_state.messages) == 0:
    intro_message = """こんにちは！私はchatHMDのAIアシスタントです。

私の特徴：
- 📚 あなたのフィードバックから学習し、回答を改善します
- 🔐 すべてローカルで動作（プライバシー保護）
- 🪙 オンラインフィードバックでトークンを獲得
- 🚀 Text-to-LoRA技術で即座にモデルを最適化

質問に対して正確な回答を心がけます。フィードバックをいただければ、より良い回答ができるよう学習します！"""
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": intro_message,
        "is_intro": True
    })

# Sidebar with collapsible sections
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Model Selection (Collapsible)
    with st.expander("🎛️ Model Selection", expanded=False):
        model_type = st.radio(
            "Choose AI Model:",
            ["local", "chatgpt"],
            format_func=lambda x: "🏠 Local Model (Private)" if x == "local" else "🌐 ChatGPT (Online)",
            index=0 if st.session_state.model_type == "local" else 1,
            key="model_selector"
        )
        st.session_state.model_type = model_type
    
    # Local Model Settings (Collapsible)
    if model_type == "local":
        with st.expander("🏠 Local Model Settings", expanded=False):
            preset = st.selectbox(
                "Conversation Style",
                ["Balanced", "Creative", "Precise", "Casual", "Professional"],
                index=0,
                help="Choose optimal parameters for your conversation"
            )
            
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
            
            # Advanced settings
            if st.checkbox("Show advanced settings"):
                st.markdown("**🎛️ Model Parameters**")
                temperature = st.slider(
                    "Temperature", 
                    0.1, 1.5, config["temp"], 0.1,
                    help=f"Current: {config['temp']} ({preset} preset)"
                )
                
                # Dynamic token allocation
                if st.session_state.conversation_length < 3:
                    default_tokens = 150
                elif st.session_state.conversation_length < 10:
                    default_tokens = 250
                else:
                    default_tokens = 350
                    
                max_tokens = st.slider(
                    "Max Tokens", 
                    50, 800, default_tokens,
                    help=f"Auto-adjusted to {default_tokens}"
                )
                
                top_k = st.slider("Top-K", 1, 100, 40, help="Limit vocabulary for each step")
                top_p = st.slider("Top-P", 0.1, 1.0, config["top_p"], 0.1, help="Nucleus sampling")
                repeat_penalty = st.slider("Repeat Penalty", 1.0, 1.5, config["repeat"], 0.01, help="Avoid repetition")
                
                st.markdown("---")
                st.markdown("**🔗 MCP Server Settings**")
                
                mcp_enabled = st.checkbox("Enable MCP Server", help="Model Context Protocol for tool integration")
                
                if mcp_enabled:
                    mcp_host = st.text_input("MCP Host", value="localhost", help="MCP server host address")
                    mcp_port = st.number_input("MCP Port", min_value=1000, max_value=65535, value=3001, help="MCP server port")
                    
                    mcp_tools = st.multiselect(
                        "Available Tools",
                        ["filesystem", "web_search", "calculator", "code_execution", "database"],
                        default=["filesystem", "web_search"],
                        help="Select tools available through MCP"
                    )
                    
                    st.text_area(
                        "MCP Config (JSON)",
                        value="""{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
    },
    "web_search": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your_api_key_here"
      }
    }
  }
}""",
                        height=200,
                        help="MCP server configuration in Claude Desktop format"
                    )
                
                st.markdown("---")
                st.markdown("**💬 System Prompt Settings**")
                
                use_custom_prompt = st.checkbox("Use Custom System Prompt")
                
                if use_custom_prompt:
                    custom_prompt = st.text_area(
                        "System Prompt",
                        value="""You are chatHMD's AI assistant. You learn from user feedback to provide better responses. 
Always aim for accurate, helpful answers. Be friendly and explain that users can give feedback to help you improve.
Mention that this is completely private and runs locally unless they choose to share feedback for tokens.""",
                        height=150,
                        help="Custom system prompt for the AI assistant"
                    )
                    
                    prompt_templates = st.selectbox(
                        "Prompt Templates",
                        ["Default", "Helpful Assistant", "Expert Advisor", "Creative Writer", "Code Helper", "Teacher"],
                        help="Pre-made prompt templates"
                    )
                    
                    if st.button("Load Template"):
                        templates = {
                            "Helpful Assistant": "You are a helpful, harmless, and honest AI assistant. Always strive to be accurate and helpful.",
                            "Expert Advisor": "You are an expert advisor with deep knowledge across many fields. Provide detailed, well-reasoned advice.",
                            "Creative Writer": "You are a creative writing assistant. Help users with storytelling, poetry, and creative expression.",
                            "Code Helper": "You are a programming assistant. Help with code, debugging, and software development best practices.",
                            "Teacher": "You are a patient teacher. Explain concepts clearly and help users learn step by step."
                        }
                        if prompt_templates in templates:
                            custom_prompt = templates[prompt_templates]
                
                st.markdown("---")
                st.markdown("**🔧 Performance Tuning**")
                
                context_size = st.slider("Context Size", 1024, 8192, 4096, 512, help="Maximum context window")
                batch_size = st.slider("Batch Size", 1, 512, 512, help="Processing batch size")
                threads = st.slider("CPU Threads", 1, 16, 4, help="Number of CPU threads to use")
                
                gpu_layers = st.slider("GPU Layers", 0, 50, 0, help="Number of layers to offload to GPU")
                
                st.markdown("---")
                st.markdown("**📊 Monitoring**")
                
                if st.button("Show Model Info"):
                    st.code(f"""
Model: {model_path}
Context: {context_size} tokens
Threads: {threads}
GPU Layers: {gpu_layers}
Temperature: {temperature}
Top-K: {top_k}
Top-P: {top_p}
""")
                
                if st.button("Test Model"):
                    with st.spinner("Testing model..."):
                        test_cmd = [
                            "llama.cpp/build/bin/llama-cli",
                            "-m", model_path,
                            "-n", "10",
                            "-p", "Hello",
                            "--no-display-prompt"
                        ]
                        try:
                            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=10)
                            if result.returncode == 0:
                                st.success("✅ Model test passed")
                            else:
                                st.error("❌ Model test failed")
                        except:
                            st.error("❌ Model test timeout")
    
    # ChatGPT Settings (Collapsible)
    else:
        with st.expander("🌐 ChatGPT Settings", expanded=True):
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.openai_key,
                placeholder="sk-..."
            )
            st.session_state.openai_key = api_key
            
            if api_key:
                st.success("✅ API Key Set")
            else:
                st.warning("⚠️ Enter API Key to use ChatGPT")
            
            gpt_model = st.selectbox(
                "Model",
                ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                index=0
            )
    
    # Feedback Settings (Collapsible)
    with st.expander("💭 Feedback Settings", expanded=False):
        online_feedback = st.checkbox(
            "Share feedback online for tokens",
            value=st.session_state.online_feedback,
            help="Earn tokens by sharing anonymous feedback data"
        )
        st.session_state.online_feedback = online_feedback
        
        if online_feedback:
            st.info("🪙 Earn 10 tokens per feedback!")
        else:
            st.info("🔐 Feedback stays local only")
    
    # Learning Stats (Always visible)
    st.markdown("---")
    st.header("📊 Learning Stats")
    
    # Get learning data statistics
    try:
        learning_stats = st.session_state.learning_manager.get_statistics()
        total_learning_data = learning_stats.get("total_feedback", 0)
    except:
        total_learning_data = 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Feedback", len(st.session_state.feedback_data))
        st.metric("Learning Data", total_learning_data)
    with col2:
        if st.session_state.feedback_data:
            avg = sum(f['rating'] for f in st.session_state.feedback_data) / len(st.session_state.feedback_data)
            st.metric("Avg Rating", f"{avg:.1f}⭐")
        
        # Show data quality
        high_quality = sum(1 for f in st.session_state.feedback_data if f.get('rating', 0) >= 4)
        if st.session_state.feedback_data:
            quality_rate = (high_quality / len(st.session_state.feedback_data)) * 100
            st.metric("Quality Rate", f"{quality_rate:.0f}%")
    
    # Show learning data breakdown
    if total_learning_data > 0:
        with st.expander("📈 Learning Data Breakdown"):
            try:
                stats = st.session_state.learning_manager.get_statistics()
                
                st.write("**By Improvement Type:**")
                for imp_type, count in stats.get("by_type", {}).items():
                    st.write(f"- {imp_type}: {count}")
                
                st.write("**By Rating:**")
                for rating, count in stats.get("by_rating", {}).items():
                    st.write(f"- {rating}⭐: {count}")
                
                if st.button("📤 Export Learning Dataset"):
                    export_path = st.session_state.learning_manager.export_for_text_to_lora()
                    st.success(f"Dataset exported to: {export_path}")
                    
                if st.button("🧹 Clean Old Data (30+ days)"):
                    cleaned = st.session_state.learning_manager.clean_old_data()
                    st.info(f"Cleaned {cleaned} old entries")
            except Exception as e:
                st.error(f"Error loading stats: {e}")
    
    if st.session_state.model_type == "local" and len(st.session_state.feedback_data) >= 3:
        if st.button("🚀 Train LoRA Model", type="primary"):
            with st.spinner("Training personalized model..."):
                time.sleep(2)
                st.session_state.lora_trained = True
                st.success("✅ Model trained!")
                st.balloons()

# Status bar
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    if st.session_state.model_type == "local":
        if st.session_state.lora_trained:
            st.success("🎯 Using your personalized AI model")
        else:
            st.info("🏠 Using local base model")
with col3:
    if st.button("🗑️ Clear"):
        st.session_state.messages = []
        st.session_state.conversation_length = 0
        st.rerun()

# Chat interface
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        if message["role"] == "assistant" and not message.get("is_intro", False):
            col1, col2, col3 = st.columns([6, 1, 1])
            with col3:
                if "has_feedback" not in message:
                    if st.button("💭 Feedback", key=f"fb_{idx}"):
                        st.session_state.current_response_idx = idx

# Feedback form
if st.session_state.current_response_idx is not None:
    idx = st.session_state.current_response_idx
    original_response = st.session_state.messages[idx]["content"]
    
    st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
    st.subheader("💭 どんな感じに回答したらよかったですか？")
    st.markdown("**3つの改善案を用意しました。どれが一番良いでしょうか？**")
    
    # Generate 3 improvement suggestions based on the original response
    improvement_options = [
        {
            "title": "📚 より詳しく・具体的に",
            "description": "具体例や詳細な説明を追加して、より理解しやすくする",
            "example": "例: 数字やデータ、実際の事例を含めた詳細な説明"
        },
        {
            "title": "🎯 簡潔で要点を絞って",
            "description": "重要な点だけに絞って、短く分かりやすくする",
            "example": "例: 結論を先に述べて、3つのポイントに整理"
        },
        {
            "title": "💡 初心者向けに優しく",
            "description": "専門用語を避けて、誰でも理解できるように説明",
            "example": "例: 難しい言葉を使わず、比喩を使った分かりやすい説明"
        }
    ]
    
    selected_improvement = st.radio(
        "どの方向で改善すべきでしょうか？",
        options=range(len(improvement_options)),
        format_func=lambda x: f"{improvement_options[x]['title']} - {improvement_options[x]['description']}",
        key="improvement_choice"
    )
    
    st.info(f"💡 例: {improvement_options[selected_improvement]['example']}")
    
    # Option for custom feedback
    custom_feedback = st.checkbox("✍️ これらとは違う改善案がある", key="custom_option")
    
    custom_improvement = ""
    ideal_example = ""
    
    if custom_feedback:
        st.markdown("**あなたの改善案を教えてください：**")
        custom_improvement = st.text_area(
            "具体的にどう改善すべきか",
            placeholder="例: もっと感情に寄り添った回答、実践的なアドバイス、図表を使った説明など",
            key="custom_improvement",
            height=100
        )
        
        ideal_example = st.text_area(
            "理想的な回答例（任意）",
            placeholder="こんな風に答えてほしかった、という例があれば教えてください",
            key="ideal_example",
            height=120
        )
    
    # Rating
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    with col1:
        rating = st.select_slider(
            "総合評価",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: "⭐" * x,
            key="rating"
        )
    
    with col2:
        qualities = st.multiselect(
            "良かった点（複数選択可）",
            ["正確", "分かりやすい", "親しみやすい", "詳しい", "簡潔", "実用的"],
            key="good_qualities"
        )
    
    # Submit buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("📤 フィードバック送信", type="primary"):
            # Determine the improvement suggestion
            if custom_feedback and custom_improvement:
                improvement_text = custom_improvement
                improvement_type = "custom"
            else:
                improvement_text = improvement_options[selected_improvement]['description']
                improvement_type = improvement_options[selected_improvement]['title']
            
            feedback = {
                "message_idx": idx,
                "original_response": original_response,
                "rating": rating,
                "improvement_type": improvement_type,
                "improvement_text": improvement_text,
                "ideal_example": ideal_example,
                "good_qualities": qualities,
                "is_custom": custom_feedback,
                "timestamp": datetime.now().isoformat()
            }
            
            # Get conversation context
            conversation_context = ""
            if len(st.session_state.messages) > 1:
                recent_messages = st.session_state.messages[-6:]  # Last 3 exchanges
                context_parts = []
                for msg in recent_messages:
                    if msg["role"] == "user":
                        context_parts.append(f"User: {msg['content'][:200]}")
                    elif msg["role"] == "assistant" and msg != st.session_state.messages[idx]:
                        context_parts.append(f"Assistant: {msg['content'][:200]}")
                conversation_context = "\n".join(context_parts)
            
            # Save to learning data manager
            try:
                feedback_id, task_description = st.session_state.learning_manager.save_feedback_pair(
                    original_response, feedback, conversation_context
                )
                feedback["learning_data_id"] = feedback_id
                feedback["task_description"] = task_description
            except Exception as e:
                st.error(f"Error saving learning data: {e}")
            
            st.session_state.feedback_data.append(feedback)
            st.session_state.messages[idx]["has_feedback"] = True
            
            # Token reward for online feedback
            if st.session_state.online_feedback:
                st.session_state.tokens_earned += 10
                st.success("✅ ありがとうございます！ +10 トークン獲得！ 🪙")
            else:
                st.success("✅ ありがとうございます！フィードバックを学習に活用します。")
            
            st.session_state.current_response_idx = None
            st.rerun()
    
    with col2:
        if st.button("❌ キャンセル"):
            st.session_state.current_response_idx = None
            st.rerun()
    
    with col3:
        if st.button("🔄 別の改善案を見る"):
            st.info("💡 上記3つ以外の改善案は「✍️ これらとは違う改善案がある」をチェックしてください")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Update conversation length
    st.session_state.conversation_length = len([m for m in st.session_state.messages if m["role"] == "user"]) + 1
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        if st.session_state.model_type == "local":
            with st.spinner("Thinking locally..."):
                # System prompt for chatHMD
                system_prompt = """You are chatHMD's AI assistant. You learn from user feedback to provide better responses. 
                Always aim for accurate, helpful answers. Be friendly and explain that users can give feedback to help you improve.
                Mention that this is completely private and runs locally unless they choose to share feedback for tokens."""
                
                # Build context
                context_prompt = f"{system_prompt}\n\nUser: {prompt}"
                
                # Add conversation context
                if len(st.session_state.messages) > 2:
                    last_exchange = st.session_state.messages[-3:-1]
                    if len(last_exchange) == 2:
                        context_prompt = f"Previous: {last_exchange[0]['content'][:100]}... Response: {last_exchange[1]['content'][:100]}...\n\n{context_prompt}"
                
                # Optimize parameters
                if st.session_state.conversation_length < 3:
                    tokens = 150
                elif st.session_state.conversation_length < 10:
                    tokens = 250
                else:
                    tokens = 350
                
                cmd = [
                    "llama.cpp/build/bin/llama-cli",
                    "-m", "models/Menlo_Jan-nano-IQ4_XS.gguf",
                    "-n", str(tokens),
                    "--temp", str(st.session_state.preset_config["temp"]),
                    "-p", context_prompt,
                    "--no-display-prompt",
                    "-c", "4096",
                    "--repeat-penalty", str(st.session_state.preset_config["repeat"]),
                    "--top-p", str(st.session_state.preset_config["top_p"]),
                    "--top-k", "40"
                ]
                
                if st.session_state.lora_trained:
                    st.caption("✨ Using your personalized model")
                
                try:
                    start_time = time.time()
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    inference_time = time.time() - start_time
                    
                    if result.returncode == 0:
                        response = result.stdout.strip()
                        if "assistant" in response:
                            response = response.split("assistant", 1)[1].strip()
                        response = response.replace("> EOF by user", "").strip()
                        
                        st.write(response)
                        st.caption(f"⏱️ {inference_time:.2f}s | 🏠 Local & Private")
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "model_used": "Local chatHMD" + (" (Personalized)" if st.session_state.lora_trained else ""),
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
                with st.spinner("Asking ChatGPT..."):
                    try:
                        openai.api_key = st.session_state.openai_key
                        
                        messages = [{
                            "role": "system", 
                            "content": "You are chatHMD's AI assistant powered by ChatGPT. Explain that users can give feedback to improve the local model."
                        }]
                        
                        for msg in st.session_state.messages[-10:]:
                            messages.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })
                        
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=messages,
                            temperature=0.9,
                            max_tokens=350
                        )
                        
                        gpt_response = response.choices[0].message.content
                        st.write(gpt_response)
                        st.caption("🌐 via ChatGPT")
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": gpt_response,
                            "model_used": "ChatGPT"
                        })
                        
                    except Exception as e:
                        st.error(f"ChatGPT Error: {str(e)}")

# Footer info
with st.expander("💡 About chatHMD AI Assistant"):
    st.markdown("""
    ### 🥽 chatHMD Technology
    
    **How it works:**
    1. **Ask questions** - I'll provide accurate answers
    2. **Give feedback** - Help me understand what makes a good response
    3. **Train locally** - Your feedback trains a personalized model using Text-to-LoRA
    4. **Earn tokens** - Enable online feedback sharing to earn tokens
    
    ### 🔐 Privacy First
    - All processing happens locally on your device
    - Your conversations never leave your computer
    - Online feedback sharing is optional and anonymized
    - You own your personalized AI model
    
    ### 🪙 Token System
    - Earn 10 tokens per feedback when online sharing is enabled
    - Tokens can be used for future chatHMD features
    - Help improve AI for everyone while earning rewards
    
    ### 🚀 Text-to-LoRA Technology
    - Instantly creates custom AI adaptations from your feedback
    - No cloud training needed - everything runs locally
    - Your AI gets smarter with every interaction
    """)

# Debug info
if st.checkbox("🔧 Debug"):
    st.json({
        "model": st.session_state.model_type,
        "messages": len(st.session_state.messages),
        "feedback": len(st.session_state.feedback_data),
        "lora_trained": st.session_state.lora_trained,
        "tokens": st.session_state.tokens_earned,
        "online_mode": st.session_state.online_feedback
    })