#!/bin/bash
# Build script for substrate MCP Docker image

echo "Building substrate MCP Docker image..."

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Build the Docker image
docker build -t substrate-mcp:latest .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "To test the image:"
    echo "docker run --rm -it -v $(pwd)/docs:/app/docs:ro substrate-mcp:latest"
    echo ""
    echo "To use in Claude Desktop, add the configuration to cline_mcp_settings.json"
else
    echo "❌ Build failed!"
    exit 1
fi
