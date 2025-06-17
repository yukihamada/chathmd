#!/usr/bin/env python3
"""
RunPod Deployment Script for jan-nano XS Model
Automatically deploys chatHMD with jan-nano model to RunPod GPU instances
"""

import os
import json
import requests
import time
from pathlib import Path

class RunPodDeployer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('RUNPOD_API_KEY')
        self.base_url = 'https://api.runpod.ai/v2'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
    def create_template(self):
        """Create RunPod template for jan-nano XS deployment"""
        template_config = {
            "name": "chatHMD-jan-nano-xs",
            "imageName": "runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04",
            "dockerArgs": "",
            "containerDiskInGb": 50,
            "volumeInGb": 10,
            "volumeMountPath": "/workspace",
            "ports": "8080/http",
            "env": [
                {
                    "key": "MODEL_NAME", 
                    "value": "jan-nano-xs"
                },
                {
                    "key": "QUANTIZATION",
                    "value": "Q4_K_XS"
                }
            ],
            "startScript": self.get_startup_script()
        }
        
        response = requests.post(
            f"{self.base_url}/user/template",
            headers=self.headers,
            json=template_config
        )
        
        if response.status_code == 200:
            template = response.json()
            print(f"✅ Template created: {template['id']}")
            return template['id']
        else:
            print(f"❌ Template creation failed: {response.text}")
            return None
    
    def get_startup_script(self):
        """Generate startup script for RunPod instance"""
        return """#!/bin/bash
set -e

echo "🚀 Starting chatHMD jan-nano XS deployment..."

# Update system
apt-get update && apt-get install -y wget curl git

# Install llama.cpp with CUDA support
cd /workspace
if [ ! -d "llama.cpp" ]; then
    echo "📦 Cloning llama.cpp..."
    git clone https://github.com/ggerganov/llama.cpp.git
fi

cd llama.cpp
echo "🔨 Building llama.cpp with CUDA support..."
make clean
make LLAMA_CUBLAS=1 -j$(nproc)

# Download jan-nano model
MODEL_DIR="/workspace/models"
mkdir -p $MODEL_DIR

if [ ! -f "$MODEL_DIR/jan-nano-xs.gguf" ]; then
    echo "📥 Downloading jan-nano XS model..."
    # Download pre-quantized model from HuggingFace
    wget -O "$MODEL_DIR/jan-nano-xs.gguf" \
        "https://huggingface.co/bartowski/Menlo-Jan-nano-14B-GGUF/resolve/main/Menlo-Jan-nano-14B-Q4_K_XS.gguf"
fi

# Create API server script
cat > /workspace/start_server.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import os
import signal
import sys

def signal_handler(sig, frame):
    print('🛑 Shutting down server...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

print("🚀 Starting jan-nano XS server...")

# Start llama.cpp server
cmd = [
    "./llama.cpp/llama-server",
    "-m", "/workspace/models/jan-nano-xs.gguf",
    "--port", "8080",
    "--host", "0.0.0.0",
    "-c", "4096",          # Context length
    "-ngl", "35",          # GPU layers
    "--threads", "8",      # CPU threads
    "--batch-size", "512", # Batch size
    "--n-predict", "500",  # Max tokens
    "--temp", "0.8",       # Temperature
    "--top-p", "0.95",     # Top-p
    "--repeat-penalty", "1.1"
]

try:
    process = subprocess.run(cmd, cwd="/workspace", check=True)
except KeyboardInterrupt:
    print("🛑 Server stopped by user")
except Exception as e:
    print(f"❌ Server error: {e}")
    sys.exit(1)
EOF

chmod +x /workspace/start_server.py

# Create health check endpoint
cat > /workspace/health_check.py << 'EOF'
#!/usr/bin/env python3
import requests
import json
import time

def check_health():
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    max_retries = 30
    for i in range(max_retries):
        if check_health():
            print("✅ Server is healthy")
            break
        print(f"⏳ Waiting for server... ({i+1}/{max_retries})")
        time.sleep(10)
    else:
        print("❌ Server health check failed")
        exit(1)
EOF

chmod +x /workspace/health_check.py

echo "✅ Setup complete! Starting server..."

# Start the server
cd /workspace
python3 start_server.py
"""

    def deploy_endpoint(self, template_id, gpu_type="NVIDIA RTX 4090"):
        """Deploy endpoint using the template with high availability"""
        endpoint_config = {
            "name": "chatHMD-jan-nano-production",
            "templateId": template_id,
            "gpuIds": gpu_type,
            "networkVolumeId": None,
            "locations": {
                "US": 2,  # Multiple US regions for redundancy
                "EU": 1   # EU backup for global coverage
            },
            "idleTimeout": 120,  # 2 minutes idle timeout (faster scaling)
            "scaleSettings": {
                "minReplicas": 1,    # Always keep 1 running (never cold start)
                "maxReplicas": 10,   # Scale up to 10 for high load
                "targetUtilization": 70,  # Scale when 70% utilized
                "scaleUpDelay": 30,      # Scale up after 30 seconds
                "scaleDownDelay": 300    # Scale down after 5 minutes
            },
            "retrySettings": {
                "maxRetries": 3,
                "retryDelay": 1000
            }
        }
        
        response = requests.post(
            f"{self.base_url}/user/endpoint",
            headers=self.headers,
            json=endpoint_config
        )
        
        if response.status_code == 200:
            endpoint = response.json()
            print(f"✅ Endpoint created: {endpoint['id']}")
            return endpoint['id']
        else:
            print(f"❌ Endpoint creation failed: {response.text}")
            return None
    
    def wait_for_deployment(self, endpoint_id, timeout=600):
        """Wait for endpoint to become ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(
                f"{self.base_url}/user/endpoint/{endpoint_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                endpoint = response.json()
                status = endpoint.get('status', 'unknown')
                
                print(f"⏳ Endpoint status: {status}")
                
                if status == 'RUNNING':
                    print(f"✅ Endpoint is ready!")
                    print(f"🌐 Endpoint URL: https://api.runpod.ai/v2/{endpoint_id}")
                    return True
                elif status == 'FAILED':
                    print(f"❌ Deployment failed")
                    return False
            
            time.sleep(30)
        
        print(f"⏰ Deployment timeout after {timeout} seconds")
        return False
    
    def test_endpoint(self, endpoint_id):
        """Test the deployed endpoint"""
        test_payload = {
            "input": {
                "prompt": "Hello! Can you tell me about privacy-first AI?",
                "max_tokens": 100,
                "temperature": 0.8
            }
        }
        
        response = requests.post(
            f"https://api.runpod.ai/v2/{endpoint_id}/runsync",
            headers=self.headers,
            json=test_payload
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'COMPLETED':
                print("✅ Test successful!")
                print(f"📝 Response: {result.get('output', {}).get('text', 'No output')}")
                return True
        
        print(f"❌ Test failed: {response.text}")
        return False
    
    def deploy(self):
        """Full deployment pipeline"""
        print("🚀 Starting chatHMD jan-nano XS deployment to RunPod...")
        
        if not self.api_key:
            print("❌ RunPod API key not found. Set RUNPOD_API_KEY environment variable.")
            return False
        
        # Create template
        template_id = self.create_template()
        if not template_id:
            return False
        
        # Deploy endpoint
        endpoint_id = self.deploy_endpoint(template_id)
        if not endpoint_id:
            return False
        
        # Wait for deployment
        if not self.wait_for_deployment(endpoint_id):
            return False
        
        # Test endpoint
        if not self.test_endpoint(endpoint_id):
            print("⚠️ Deployment successful but test failed")
        
        print(f"""
🎉 Deployment Complete!

📋 Summary:
- Template ID: {template_id}
- Endpoint ID: {endpoint_id}
- Model: jan-nano XS (Q4_K_XS)
- GPU: NVIDIA RTX 4090
- API URL: https://api.runpod.ai/v2/{endpoint_id}

🔧 Next Steps:
1. Add this endpoint ID to your Cloudflare environment variables:
   RUNPOD_ENDPOINT={endpoint_id}

2. Test the endpoint:
   curl -X POST https://api.runpod.ai/v2/{endpoint_id}/runsync \\
     -H "Authorization: Bearer YOUR_API_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{{"input": {{"prompt": "Hello!", "max_tokens": 100}}}}'

3. Monitor usage at: https://runpod.io/console/endpoints
""")
        
        return True

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy chatHMD to RunPod')
    parser.add_argument('--api-key', help='RunPod API key')
    parser.add_argument('--gpu', default='NVIDIA RTX 4090', help='GPU type')
    
    args = parser.parse_args()
    
    deployer = RunPodDeployer(args.api_key)
    success = deployer.deploy()
    
    if success:
        print("✅ All done! Your chatHMD is ready on RunPod.")
    else:
        print("❌ Deployment failed. Check the logs above.")
        exit(1)

if __name__ == "__main__":
    main()