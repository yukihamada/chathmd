#!/bin/bash
# Final deployment after GitHub security approval

echo "🚀 Final secure deployment..."

# Push to GitHub
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    
    # Create release
    echo "🏷️ Creating v1.0.0 release..."
    git tag v1.0.0
    git push origin v1.0.0
    
    # Run secure deployment
    echo "🔐 Running secure deployment script..."
    ./deploy_secure.sh
    
    echo "🎉 Full deployment completed!"
else
    echo "❌ Push failed. Check GitHub security approval."
fi