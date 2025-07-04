#!/bin/bash

echo "🚀 Setting up GPO Local Brain..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker found"

# Create directory for Local Brain
mkdir -p gpo_local_brain
cd gpo_local_brain

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# GPO Cloud Connection
CLOUD_GPO_URL=https://your-app-name.onrender.com
API_KEY=your_api_key_here

# Local Brain Settings
ORGANIZATION_ID=your_org_id
POLL_INTERVAL=30

# Document Storage
DOCUMENTS_PATH=/app/documents
PROCESSING_PATH=/app/processing

# Debug (set to False for production)
DEBUG=True
EOF
    echo "✅ Created .env file - PLEASE EDIT IT with your settings"
else
    echo "✅ .env file already exists"
fi

# Create documents directory
mkdir -p documents processing

echo "🐳 Pulling GPO Local Brain Docker image..."
docker pull gpo/local-brain:latest

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your Cloud GPO URL and API key"
echo "2. Run: ./start_local_brain.sh"
echo ""
echo "📂 Place documents to process in: ./documents/"
echo "📊 Check processing status in Cloud GPO dashboard" 