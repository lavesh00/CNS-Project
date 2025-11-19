#!/bin/bash
# Setup script for Agent Lucky

set -e

echo "🍀 Setting up Agent Lucky..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting." >&2; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git is required but not installed. Aborting." >&2; exit 1; }

echo "✅ Prerequisites check passed"

# Setup Python backend
echo "📦 Installing Python dependencies..."
cd backend
python3 -m pip install -r requirements.txt
cd ..

echo "✅ Python backend setup complete"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ~/.agent-lucky/models
mkdir -p ~/.agent-lucky/index

echo "✅ Directories created"

# Optional: Download a default model
echo "Would you like to download Code Llama 7B (4GB)? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "📥 Downloading Code Llama 7B..."
    python3 -c "
import asyncio
from backend.models.manager import ModelManager

async def download():
    manager = ModelManager()
    await manager.initialize()
    success = await manager.download_model('codellama-7b-q4')
    if success:
        print('✅ Model downloaded successfully')
    else:
        print('❌ Model download failed')

asyncio.run(download())
"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the backend:"
echo "  cd backend"
echo "  python main.py"
echo ""
echo "Happy coding with Agent Lucky! 🍀"

