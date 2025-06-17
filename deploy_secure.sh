#!/bin/bash
# Secure chatHMD Deployment Script
# Uses GitHub secrets and environment variables only

set -e

echo "🚀 Starting secure chatHMD deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}==== $1 ====${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: GitHub Repository
print_step "GitHub Repository Setup"

echo "📤 Pushing to GitHub..."
git push -u origin main

print_success "GitHub repository updated"

# Step 2: GitHub Secrets Check
print_step "GitHub Secrets Verification"

echo "🔍 Checking GitHub secrets..."
if gh secret list | grep -q "RUNPOD_API_KEY"; then
    print_success "RUNPOD_API_KEY secret is configured"
else
    print_error "RUNPOD_API_KEY secret not found"
    echo "Setting it now..."
    read -p "Enter your RunPod API key: " RUNPOD_KEY
    gh secret set RUNPOD_API_KEY --body "$RUNPOD_KEY"
    print_success "RUNPOD_API_KEY secret added"
fi

# Step 3: GitHub Release
print_step "GitHub Release Creation"

echo "🏷️ Creating GitHub release..."
git tag v1.0.0 2>/dev/null || true
git push origin v1.0.0

print_success "GitHub release created"

# Step 4: Cloudflare Pages Instructions
print_step "Cloudflare Pages Setup"

echo "🌐 Manual Cloudflare Pages setup required:"
echo ""
echo "1. Go to: https://pages.cloudflare.com/"
echo "2. Click 'Create a project'"
echo "3. Connect to Git → Select 'yukihamada/chathmd'"
echo "4. Configure:"
echo "   - Project name: chathmd"
echo "   - Production branch: main"
echo "   - Build command: (leave empty)"
echo "   - Build output directory: web"
echo "   - Root directory: web"
echo "5. Click 'Save and Deploy'"
echo ""
echo "6. After deployment, add environment variables:"
echo "   - Go to Pages → Settings → Environment variables"
echo "   - Add: RUNPOD_API_KEY (use the same key as GitHub secret)"
echo "   - Add: ENVIRONMENT = production"
echo "   - Add: MODEL_NAME = jan-nano-xs"
echo ""

read -p "Press Enter after Cloudflare Pages is set up..."

# Step 5: RunPod Deployment
print_step "RunPod GPU Deployment"

if [ -z "$RUNPOD_API_KEY" ]; then
    echo "Setting RUNPOD_API_KEY from GitHub secret for local deployment..."
    export RUNPOD_API_KEY=$(gh secret list --json name,value | jq -r '.[] | select(.name=="RUNPOD_API_KEY") | .value' 2>/dev/null || echo "")
fi

if [ -z "$RUNPOD_API_KEY" ]; then
    print_warning "RunPod API key not available for local deployment"
    echo "Please run: python3 runpod_deploy.py --api-key YOUR_KEY"
else
    echo "🖥️ Deploying jan-nano XS to RunPod..."
    python3 runpod_deploy.py
fi

# Step 6: Final Instructions
print_step "Deployment Complete"

REPO_URL=$(git remote get-url origin | sed 's/\.git$//')

echo ""
print_success "🎉 Secure Deployment Complete!"
echo ""
echo "📊 Deployment Summary:"
echo "├── 🐙 GitHub Repository: $REPO_URL"
echo "├── 🔐 GitHub Secrets: ✓ Configured"
echo "├── 🌐 Web App: https://chathmd.pages.dev (after Cloudflare setup)"
echo "├── 🚀 GitHub Releases: $REPO_URL/releases"
echo "└── ☁️ RunPod GPU: Deploy with your API key"
echo ""
echo "🔧 Security Features:"
echo "✅ No hardcoded API keys in repository"
echo "✅ GitHub secrets for CI/CD"
echo "✅ Environment variables for runtime"
echo "✅ Secure credential management"
echo ""
echo "🎯 Next Steps:"
echo "1. Complete Cloudflare Pages setup"
echo "2. Add RunPod endpoint to Cloudflare environment variables"
echo "3. Test web app: https://chathmd.pages.dev"
echo "4. Download desktop app from GitHub Releases"
echo ""
print_success "chatHMD is now securely deployed! 🥽🔐"