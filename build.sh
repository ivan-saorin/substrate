#!/bin/bash
# Build substrate Docker image

echo "Building substrate MCP Docker image..."

# Build the image
docker build -t substrate-mcp:latest .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "You can now run different instances:"
    echo ""
    echo "# Substrate (full):"
    echo "docker run -it --rm -e INSTANCE_TYPE=substrate substrate-mcp:latest"
    echo ""
    echo "# TLOEN (site formatter):"
    echo "docker run -it --rm -e INSTANCE_TYPE=tloen -e INSTANCE_DESCRIPTION='Site format transformation service' substrate-mcp:latest"
    echo ""
    echo "# UQBAR (persona manager):"
    echo "docker run -it --rm -e INSTANCE_TYPE=uqbar -e INSTANCE_DESCRIPTION='Persona and component composition service' substrate-mcp:latest"
else
    echo "❌ Build failed!"
    exit 1
fi
