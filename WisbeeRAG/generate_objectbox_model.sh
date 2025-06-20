#!/bin/bash

# ObjectBox code generation script
echo "🐝 Generating ObjectBox model..."

cd "$(dirname "$0")"

# Generate ObjectBox model
if ! command -v Sourcery &> /dev/null
then
    echo "Installing Sourcery..."
    brew install sourcery
fi

# Create ObjectBox configuration
cat > .sourcery.yml << EOF
sources:
  - Sources
templates:
  - /usr/local/lib/node_modules/objectbox-generator/templates
output: Sources/generated
EOF

echo "✅ ObjectBox setup complete"
echo "Note: You'll need to manually run ObjectBox code generation or use @objc annotations"