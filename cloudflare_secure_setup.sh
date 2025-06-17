#!/bin/bash
# Secure Cloudflare Pages Environment Variables Setup
# Does not contain hardcoded API keys

set -e

echo "🔧 Setting up Cloudflare Pages environment variables securely..."

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "📦 Installing Wrangler CLI..."
    npm install -g wrangler
fi

# Login to Cloudflare (if not already logged in)
echo "🔐 Checking Cloudflare authentication..."
if ! wrangler whoami &> /dev/null; then
    echo "Please login to Cloudflare:"
    wrangler login
fi

# Get RunPod API key from user
echo "🔑 RunPod API Key Setup"
echo "Please enter your RunPod API key:"
read -s RUNPOD_API_KEY

if [ -z "$RUNPOD_API_KEY" ]; then
    echo "❌ No API key provided. Exiting."
    exit 1
fi

# Set production environment variables
echo "⚙️ Setting production environment variables..."

# RunPod API Key
wrangler pages secret put RUNPOD_API_KEY --project-name=chathmd << EOF
${RUNPOD_API_KEY}
EOF

echo "✅ RUNPOD_API_KEY configured"

# Environment identifier
wrangler pages secret put ENVIRONMENT --project-name=chathmd << EOF
production
EOF

echo "✅ ENVIRONMENT configured"

# Model configuration
wrangler pages secret put MODEL_NAME --project-name=chathmd << EOF
jan-nano-xs
EOF

echo "✅ MODEL_NAME configured"

wrangler pages secret put MAX_TOKENS --project-name=chathmd << EOF
500
EOF

echo "✅ MAX_TOKENS configured"

wrangler pages secret put DEFAULT_TEMPERATURE --project-name=chathmd << EOF
0.8
EOF

echo "✅ DEFAULT_TEMPERATURE configured"

echo """
🎉 Cloudflare secure environment setup complete!

📋 Configured variables:
- RUNPOD_API_KEY: ✓ Set (from user input)
- ENVIRONMENT: production
- MODEL_NAME: jan-nano-xs
- MAX_TOKENS: 500
- DEFAULT_TEMPERATURE: 0.8

🔄 Next steps:
1. Deploy RunPod endpoint: python3 runpod_deploy.py
2. Update RUNPOD_ENDPOINT variable with the endpoint ID
3. Test the integration

💡 To update RUNPOD_ENDPOINT after deployment:
wrangler pages secret put RUNPOD_ENDPOINT --project-name=chathmd
"""

# Function to update endpoint after deployment
cat > update_endpoint_secure.sh << 'EOF'
#!/bin/bash
# Update RunPod endpoint ID after deployment

if [ -z "$1" ]; then
    echo "Usage: ./update_endpoint_secure.sh ENDPOINT_ID"
    exit 1
fi

ENDPOINT_ID="$1"

echo "🔄 Updating RUNPOD_ENDPOINT to: $ENDPOINT_ID"

wrangler pages secret put RUNPOD_ENDPOINT --project-name=chathmd << EOL
${ENDPOINT_ID}
EOL

echo "✅ RUNPOD_ENDPOINT updated successfully!"
echo "🌐 Your chatHMD web app is now fully configured for RunPod integration."
EOF

chmod +x update_endpoint_secure.sh

echo "📝 Created update_endpoint_secure.sh script for after RunPod deployment"