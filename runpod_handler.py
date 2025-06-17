#!/usr/bin/env python3
"""
RunPod Handler for Wisbee AI
Optimized for jan-nano XS model with llama.cpp backend
"""

import runpod
import subprocess
import os
import json
import requests
from typing import Dict, Any
import tempfile
import shutil

# Model configuration
MODEL_URL = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_PATH = "/workspace/model.gguf"
LLAMA_CPP_PATH = "/workspace/llama.cpp"

def download_model():
    """Download the quantized model if not exists"""
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading model from {MODEL_URL}...")
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()
        
        with open(MODEL_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Model downloaded to {MODEL_PATH}")
    else:
        print("Model already exists")

def setup_llama_cpp():
    """Setup llama.cpp if not exists"""
    if not os.path.exists(LLAMA_CPP_PATH):
        print("Setting up llama.cpp...")
        
        # Clone llama.cpp
        subprocess.run([
            "git", "clone", 
            "https://github.com/ggerganov/llama.cpp.git",
            LLAMA_CPP_PATH
        ], check=True)
        
        # Build llama.cpp with CUDA support
        os.chdir(LLAMA_CPP_PATH)
        subprocess.run(["make", "LLAMA_CUDA=1"], check=True)
        
        print("llama.cpp setup complete")
    else:
        print("llama.cpp already exists")

def handler(job):
    """
    RunPod handler function
    Expected input format:
    {
        "prompt": "User message",
        "max_tokens": 500,
        "temperature": 0.8,
        "top_p": 0.95,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    }
    """
    try:
        # Get job input
        job_input = job["input"]
        prompt = job_input.get("prompt", "")
        max_tokens = job_input.get("max_tokens", 500)
        temperature = job_input.get("temperature", 0.8)
        top_p = job_input.get("top_p", 0.95)
        
        # Format prompt for Wisbee
        formatted_prompt = f"""You are Wisbee, a helpful AI assistant powered by jan-nano XS model. You prioritize user privacy and provide accurate, helpful responses.

User: {prompt}
Assistant:"""
        
        # Create temp file for prompt
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write(formatted_prompt)
            prompt_file = tmp.name
        
        # Run inference with llama.cpp
        cmd = [
            f"{LLAMA_CPP_PATH}/main",
            "-m", MODEL_PATH,
            "-f", prompt_file,
            "-n", str(max_tokens),
            "--temp", str(temperature),
            "--top-p", str(top_p),
            "-c", "2048",  # Context size
            "--gpu-layers", "35",  # Offload layers to GPU
            "-b", "512",  # Batch size
            "--no-display-prompt"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        
        # Execute llama.cpp
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Clean up temp file
        os.unlink(prompt_file)
        
        # Extract response
        response = result.stdout.strip()
        
        # Remove any remaining prompt artifacts
        if "Assistant:" in response:
            response = response.split("Assistant:")[-1].strip()
        
        # Return response
        return {
            "response": response,
            "model": "jan-nano-xs",
            "tokens_generated": len(response.split()),  # Approximate
            "status": "success"
        }
        
    except subprocess.CalledProcessError as e:
        print(f"llama.cpp error: {e}")
        print(f"stderr: {e.stderr}")
        return {
            "error": f"Model inference failed: {e.stderr}",
            "status": "error"
        }
    except Exception as e:
        print(f"Handler error: {e}")
        return {
            "error": str(e),
            "status": "error"
        }

# Initialize on container start
print("Initializing Wisbee AI handler...")
download_model()
setup_llama_cpp()
print("Initialization complete!")

# Start RunPod serverless handler
runpod.serverless.start({"handler": handler})