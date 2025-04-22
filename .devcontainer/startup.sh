#!/bin/bash
# Startup script for Codespace

# Add Poetry to PATH
export PATH="/home/vscode/.local/bin:$PATH"
echo 'export PATH="/home/vscode/.local/bin:$PATH"' >> ~/.bashrc

# Start the services
docker compose up -d

# Print welcome message
echo "============================================="
echo "🎨 Sketch-to-Animated-Drawing Environment 🎨"
echo "============================================="
echo ""
echo "Environment is ready! To complete setup, run:"
echo ""
echo "bash /workspaces/sketch-to-animated-drawing/scripts/setup.sh"
echo ""
echo "This will install all dependencies and set up Minio bucket."
echo "============================================="
