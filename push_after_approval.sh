#!/bin/bash
# Push after GitHub security approval

echo "🚀 Pushing to GitHub after security approval..."

git push -u origin main --force

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    
    # Create release
    echo "🏷️ Creating v1.0.0 release..."
    git tag v1.0.0
    git push origin v1.0.0
    
    echo "🎉 GitHub setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Cloudflare Pages: https://pages.cloudflare.com/"
    echo "2. Connect Git → yukihamada/chathmd"
    echo "3. Root directory: web"
    echo "4. Add environment variable: RUNPOD_API_KEY=[Use your RunPod API key]"
    echo ""
    echo "🌐 Repository: https://github.com/yukihamada/chathmd"
else
    echo "❌ Push failed. Please check the error above."
fi