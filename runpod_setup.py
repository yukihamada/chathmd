#!/usr/bin/env python3
"""
RunPod Setup Script for Wisbee AI
Deploys jan-nano XS model on RunPod serverless infrastructure
"""

import os
import json
import requests
from typing import Dict, Any

# RunPod configuration
RUNPOD_CONFIG = {
    "name": "wisbee-jan-nano-xs",
    "image": "runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel",
    "gpu_type": "NVIDIA RTX A4000",  # Cost-effective for inference
    "container_disk_in_gb": 20,
    "volume_in_gb": 50,  # For model storage
    "min_workers": 0,  # Scale to zero when not in use
    "max_workers": 3,  # Auto-scale based on demand
    "idle_timeout": 30,  # Seconds before scaling down
    "env_vars": {
        "MODEL_NAME": "jan-nano-xs",
        "QUANTIZATION": "Q4_K_XS",
        "MAX_TOKENS": 2048,
        "TEMPERATURE": 0.8
    }
}

# Handler code for RunPod
HANDLER_CODE = '''
import runpod
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

# Initialize model
model_name = os.environ.get("MODEL_NAME", "jan-nano-xs")
model = None
tokenizer = None

def load_model():
    global model, tokenizer
    print(f"Loading model: {model_name}")
    
    # Load quantized model
    model = AutoModelForCausalLM.from_pretrained(
        f"/models/{model_name}",
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True
    )
    
    tokenizer = AutoTokenizer.from_pretrained(f"/models/{model_name}")
    print("Model loaded successfully!")

def handler(job):
    """RunPod handler function"""
    global model, tokenizer
    
    # Load model on first request
    if model is None:
        load_model()
    
    job_input = job["input"]
    prompt = job_input.get("prompt", "")
    max_tokens = job_input.get("max_tokens", 500)
    temperature = job_input.get("temperature", 0.8)
    
    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate response
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decode response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Remove the input prompt from response
    if response.startswith(prompt):
        response = response[len(prompt):].strip()
    
    return {
        "response": response,
        "model": model_name,
        "tokens_generated": len(outputs[0]) - len(inputs["input_ids"][0])
    }

runpod.serverless.start({"handler": handler})
'''

# Dockerfile for the container
DOCKERFILE = '''
FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel

# Install dependencies
RUN pip install --upgrade pip && \
    pip install transformers accelerate bitsandbytes sentencepiece protobuf

# Create model directory
RUN mkdir -p /models/jan-nano-xs

# Download the quantized model (you'll need to host this)
# ADD https://your-model-host.com/jan-nano-xs-q4.bin /models/jan-nano-xs/

# Copy handler
COPY handler.py /

# Set working directory
WORKDIR /

CMD ["python", "-u", "handler.py"]
'''

def create_runpod_endpoint():
    """Create RunPod serverless endpoint"""
    
    print("🚀 Setting up RunPod endpoint for Wisbee AI...")
    
    # Check for API key
    api_key = os.environ.get("RUNPOD_API_KEY")
    if not api_key:
        print("❌ RUNPOD_API_KEY environment variable not set!")
        print("Get your API key from: https://runpod.io/console/user/settings")
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Create serverless endpoint
    endpoint_data = {
        "name": RUNPOD_CONFIG["name"],
        "dockerImage": RUNPOD_CONFIG["image"],
        "gpuType": RUNPOD_CONFIG["gpu_type"],
        "containerDiskInGb": RUNPOD_CONFIG["container_disk_in_gb"],
        "volumeInGb": RUNPOD_CONFIG["volume_in_gb"],
        "minWorkers": RUNPOD_CONFIG["min_workers"],
        "maxWorkers": RUNPOD_CONFIG["max_workers"],
        "idleTimeout": RUNPOD_CONFIG["idle_timeout"],
        "env": RUNPOD_CONFIG["env_vars"],
        "scalerType": "QUEUE_DEPTH",
        "scalerValue": 1  # Scale up when 1 request in queue
    }
    
    try:
        response = requests.post(
            "https://api.runpod.ai/v2/serverless/create",
            headers=headers,
            json=endpoint_data
        )
        response.raise_for_status()
        
        result = response.json()
        endpoint_id = result.get("id")
        
        print(f"✅ RunPod endpoint created successfully!")
        print(f"📍 Endpoint ID: {endpoint_id}")
        print(f"🔗 Endpoint URL: https://api.runpod.ai/v2/{endpoint_id}/runsync")
        
        # Save configuration
        config = {
            "endpoint_id": endpoint_id,
            "endpoint_url": f"https://api.runpod.ai/v2/{endpoint_id}/runsync",
            "config": RUNPOD_CONFIG
        }
        
        with open("runpod_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print("\n📝 Configuration saved to runpod_config.json")
        print("\n🔧 Next steps:")
        print("1. Set RUNPOD_ENDPOINT in Cloudflare Pages environment")
        print(f"   RUNPOD_ENDPOINT={endpoint_id}")
        print("2. Upload the model to RunPod volume")
        print("3. Deploy the handler code")
        
        return endpoint_id
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating RunPod endpoint: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def test_endpoint(endpoint_id: str):
    """Test the RunPod endpoint"""
    
    api_key = os.environ.get("RUNPOD_API_KEY")
    if not api_key:
        print("❌ RUNPOD_API_KEY not set!")
        return
    
    print(f"\n🧪 Testing endpoint {endpoint_id}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    test_payload = {
        "input": {
            "prompt": "Hello! Can you introduce yourself?",
            "max_tokens": 100,
            "temperature": 0.8
        }
    }
    
    try:
        response = requests.post(
            f"https://api.runpod.ai/v2/{endpoint_id}/runsync",
            headers=headers,
            json=test_payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("status") == "COMPLETED":
            print("✅ Test successful!")
            print(f"Response: {result.get('output', {}).get('response', 'No response')}")
        else:
            print(f"⚠️ Test returned status: {result.get('status')}")
            print(f"Details: {result}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Test failed: {e}")

def main():
    """Main setup function"""
    
    print("🐝 Wisbee AI - RunPod Setup")
    print("=" * 50)
    
    # Save handler code
    with open("handler.py", "w") as f:
        f.write(HANDLER_CODE)
    print("✅ Handler code saved to handler.py")
    
    # Save Dockerfile
    with open("Dockerfile", "w") as f:
        f.write(DOCKERFILE)
    print("✅ Dockerfile saved")
    
    # Create endpoint
    endpoint_id = create_runpod_endpoint()
    
    if endpoint_id:
        # Test the endpoint
        input("\n⏸️  Press Enter to test the endpoint (make sure it's deployed first)...")
        test_endpoint(endpoint_id)

if __name__ == "__main__":
    main()