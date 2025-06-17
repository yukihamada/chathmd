#!/bin/bash
# Deploy Wisbee AI to RunPod

echo "🐝 Deploying Wisbee AI to RunPod..."

# Check for API key
if [ -z "$RUNPOD_API_KEY" ]; then
    echo "❌ Error: RUNPOD_API_KEY environment variable not set"
    echo "Get your API key from: https://runpod.io/console/user/settings"
    exit 1
fi

# Build Docker image
echo "🔨 Building Docker image..."
docker build -f Dockerfile.runpod -t wisbee-runpod:latest .

# Tag for RunPod registry (replace with your Docker Hub username)
DOCKER_USERNAME=${DOCKER_USERNAME:-"wisbeeai"}
docker tag wisbee-runpod:latest $DOCKER_USERNAME/wisbee-runpod:latest

# Push to Docker Hub (requires docker login)
echo "📤 Pushing to Docker Hub..."
docker push $DOCKER_USERNAME/wisbee-runpod:latest

# Create RunPod serverless endpoint
echo "🚀 Creating RunPod endpoint..."

ENDPOINT_CONFIG='{
  "name": "wisbee-jan-nano-xs",
  "dockerImage": "'$DOCKER_USERNAME'/wisbee-runpod:latest",
  "gpuType": "NVIDIA RTX A4000",
  "containerDiskInGb": 20,
  "volumeInGb": 50,
  "minWorkers": 0,
  "maxWorkers": 3,
  "idleTimeout": 30,
  "scalerType": "QUEUE_DEPTH",
  "scalerValue": 1,
  "env": {
    "MODEL_NAME": "jan-nano-xs",
    "QUANTIZATION": "Q4_K_M"
  }
}'

# Create endpoint via API
RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$ENDPOINT_CONFIG" \
  https://api.runpod.ai/v2/serverless/create)

# Extract endpoint ID
ENDPOINT_ID=$(echo $RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -z "$ENDPOINT_ID" ]; then
    echo "❌ Failed to create endpoint"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "✅ RunPod endpoint created!"
echo "📍 Endpoint ID: $ENDPOINT_ID"
echo "🔗 Endpoint URL: https://api.runpod.ai/v2/$ENDPOINT_ID/runsync"

# Save configuration
cat > runpod_config.json <<EOF
{
  "endpoint_id": "$ENDPOINT_ID",
  "endpoint_url": "https://api.runpod.ai/v2/$ENDPOINT_ID/runsync",
  "docker_image": "$DOCKER_USERNAME/wisbee-runpod:latest",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "📝 Configuration saved to runpod_config.json"

# Update Cloudflare environment
echo ""
echo "🔧 Next steps:"
echo "1. Add to Cloudflare Pages environment variables:"
echo "   RUNPOD_API_KEY=$RUNPOD_API_KEY"
echo "   RUNPOD_ENDPOINT=$ENDPOINT_ID"
echo ""
echo "2. Test the endpoint:"
echo "   curl -X POST https://api.runpod.ai/v2/$ENDPOINT_ID/runsync \\"
echo "     -H 'Authorization: Bearer $RUNPOD_API_KEY' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"input\": {\"prompt\": \"Hello!\", \"max_tokens\": 50}}'"