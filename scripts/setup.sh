#!/bin/bash
# Setup script for Sketch-to-Animated-Drawing project

set -e

echo "🔧 Setting up Sketch-to-Animated-Drawing environment..."

# Make sure we're in the project root
cd /workspaces/sketch-to-animated-drawing

# Ensure Poetry is in PATH
export PATH="/home/vscode/.local/bin:$PATH"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
poetry install

# Create Minio bucket
echo "🪣 Setting up Minio bucket..."
pip install mc &>/dev/null || echo "mc already installed"
mc alias set myminio http://localhost:9000 minioadmin minioadmin
mc mb myminio/sketches --ignore-existing || echo "Bucket already exists"

# Install frontend dependencies
echo "🌐 Installing frontend dependencies..."
cd frontend
pnpm install

echo "✅ Setup complete!"
echo ""
echo "To start the application, run these commands in separate terminals:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd /workspaces/sketch-to-animated-drawing"
echo "  poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Terminal 2 (Worker):"
echo "  cd /workspaces/sketch-to-animated-drawing"
echo "  poetry run celery -A app.tasks worker --loglevel=info"
echo ""
echo "Terminal 3 (Frontend):"
echo "  cd /workspaces/sketch-to-animated-drawing/frontend"
echo "  pnpm dev"
echo ""
echo "Access the application at port 5173"
