import streamlit as st
import subprocess
import json
from pathlib import Path
import time
from scripts.generate_lora import TextToLoRA

st.set_page_config(
    page_title="Text-to-LoRA with jan-mini",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'current_lora' not in st.session_state:
    st.session_state.current_lora = None
if 'generated_loras' not in st.session_state:
    st.session_state.generated_loras = []

st.title("🤖 Text-to-LoRA with jan-mini-14B")
st.markdown("Generate task-specific LoRA adapters from natural language descriptions")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    model_path = st.text_input(
        "Model Path", 
        value="models/Menlo_Jan-nano-IQ4_XS.gguf",
        help="Path to the quantized GGUF model"
    )
    
    hypernet_path = st.text_input(
        "Hypernet Path",
        value="trained_t2l/jan_qwen_t2l",
        help="Path to the Text-to-LoRA hypernet"
    )
    
    lora_rank = st.slider(
        "LoRA Rank",
        min_value=4, max_value=32, value=8,
        help="Higher rank = better quality but more memory"
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.1, max_value=2.0, value=0.8, step=0.1,
        help="Controls randomness of generation"
    )
    
    max_tokens = st.slider(
        "Max Tokens",
        min_value=50, max_value=500, value=200,
        help="Maximum number of tokens to generate"
    )

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 LoRA Generation")
    
    task_description = st.text_area(
        "Task Description",
        placeholder="例: 高校入試レベルの長文を80語以内で要約する",
        height=100,
        help="Describe the task you want the model to perform"
    )
    
    lora_name = st.text_input(
        "LoRA Name",
        placeholder="e.g., summarizer_v1",
        help="Name for the generated LoRA adapter"
    )
    
    if st.button("🚀 Generate LoRA", disabled=not (task_description and lora_name)):
        with st.spinner("Generating LoRA adapter..."):
            try:
                # Generate LoRA
                generator = TextToLoRA(hypernet_path)
                lora_weights = generator.generate_lora_weights(task_description, rank=lora_rank)
                output_path = Path(f"loras/{lora_name}")
                generator.save_lora_adapter(lora_weights, output_path, task_description)
                
                st.success(f"✅ LoRA adapter generated: {output_path}")
                st.session_state.generated_loras.append({
                    "name": lora_name,
                    "path": str(output_path),
                    "description": task_description
                })
            except Exception as e:
                st.error(f"Error generating LoRA: {e}")
    
    # Display generated LoRAs
    if st.session_state.generated_loras:
        st.subheader("📚 Generated LoRAs")
        for lora in st.session_state.generated_loras:
            with st.expander(f"🔸 {lora['name']}"):
                st.write(f"**Description:** {lora['description']}")
                st.write(f"**Path:** `{lora['path']}`")
                if st.button(f"Load {lora['name']}", key=f"load_{lora['name']}"):
                    st.session_state.current_lora = lora['path']
                    st.success(f"Loaded LoRA: {lora['name']}")

with col2:
    st.header("💬 Interactive Inference")
    
    # Display current LoRA
    if st.session_state.current_lora:
        st.info(f"🔹 Current LoRA: {Path(st.session_state.current_lora).name}")
        if st.button("❌ Remove LoRA"):
            st.session_state.current_lora = None
            st.success("LoRA removed")
    else:
        st.info("🔸 No LoRA loaded (using base model)")
    
    # Inference input
    prompt = st.text_area(
        "Prompt",
        placeholder="Enter your prompt here...",
        height=100
    )
    
    if st.button("🎯 Generate", disabled=not prompt):
        with st.spinner("Generating response..."):
            try:
                # Build command
                cmd = [
                    "llama.cpp/build/bin/llama-cli",
                    "-m", model_path,
                    "-n", str(max_tokens),
                    "--temp", str(temperature),
                    "-p", prompt,
                    "--no-display-prompt"
                ]
                
                # Add LoRA if loaded
                if st.session_state.current_lora:
                    # For now, we'll skip GGUF conversion
                    st.warning("Note: LoRA is loaded but GGUF conversion not implemented in this demo")
                
                # Run inference
                start_time = time.time()
                result = subprocess.run(cmd, capture_output=True, text=True)
                inference_time = time.time() - start_time
                
                if result.returncode == 0:
                    # Extract the generated text
                    output = result.stdout.strip()
                    
                    # Display response
                    st.subheader("🤖 Response")
                    st.write(output)
                    
                    # Show metrics
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Inference Time", f"{inference_time:.2f}s")
                    with col_b:
                        tokens = len(output.split())
                        st.metric("Tokens/sec", f"{tokens/inference_time:.1f}")
                else:
                    st.error(f"Error: {result.stderr}")
                    
            except Exception as e:
                st.error(f"Error during inference: {e}")

# Footer
st.markdown("---")
st.markdown("""
### 📖 Quick Guide
1. **Generate LoRA**: Enter a task description and click "Generate LoRA"
2. **Load LoRA**: Click on a generated LoRA to load it
3. **Test**: Enter a prompt and click "Generate" to see the response

### 🛠️ Model Info
- **Base Model**: jan-mini-14B (Menlo variant)
- **Quantization**: IQ4_XS (4.25 bpw)
- **Size**: ~2.1 GB
""")

# Debug info (collapsible)
with st.expander("🐛 Debug Info"):
    st.write("**Model exists:**", Path(model_path).exists())
    st.write("**Hypernet exists:**", Path(hypernet_path).exists())
    st.write("**llama-cli exists:**", Path("llama.cpp/build/bin/llama-cli").exists())
    st.write("**Generated LoRAs:**", len(st.session_state.generated_loras))