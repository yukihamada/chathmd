#!/bin/bash
# Quick deployment after GitHub repo creation

echo "🚀 Starting immediate deployment..."

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ GitHub push successful!"
    
    # Create GitHub release
    echo "🏷️ Creating GitHub release..."
    git tag v1.0.0
    git push origin v1.0.0
    
    echo "🎉 GitHub setup complete!"
    echo ""
    echo "🌐 Next steps:"
    echo "1. Go to https://pages.cloudflare.com/"
    echo "2. Connect Git → yukihamada/chathmd"
    echo "3. Root directory: web"
    echo "4. Deploy!"
    echo ""
    echo "📋 URLs:"
    echo "- Repository: https://github.com/yukihamada/chathmd"
    echo "- Releases: https://github.com/yukihamada/chathmd/releases"
    echo "- Web App: https://chathmd.pages.dev (after Cloudflare setup)"
    
else
    echo "❌ GitHub push failed. Please create the repository first:"
    echo "https://github.com/new"
fi