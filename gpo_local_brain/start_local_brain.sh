#!/bin/bash

echo "🚀 Starting GPO Local Brain..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run setup.sh first."
    exit 1
fi

# Load environment variables
source .env

# Validate required variables
if [ -z "$CLOUD_GPO_URL" ] || [ -z "$API_KEY" ] || [ -z "$ORGANIZATION_ID" ]; then
    echo "❌ Missing required environment variables. Please edit .env file:"
    echo "   - CLOUD_GPO_URL"
    echo "   - API_KEY" 
    echo "   - ORGANIZATION_ID"
    exit 1
fi

echo "✅ Environment variables loaded"
echo "🔗 Cloud GPO: $CLOUD_GPO_URL"
echo "🏢 Organization: $ORGANIZATION_ID"

# Create directories if they don't exist
mkdir -p documents processing

# Stop existing container if running
docker stop gpo-local-brain 2>/dev/null || true
docker rm gpo-local-brain 2>/dev/null || true

echo "🐳 Starting Docker container..."

# Run the Local Brain container
docker run -d \
    --name gpo-local-brain \
    --restart unless-stopped \
    --env-file .env \
    -v "$(pwd)/documents:/app/documents" \
    -v "$(pwd)/processing:/app/processing" \
    -p 8080:8080 \
    gpo/local-brain:latest

if [ $? -eq 0 ]; then
    echo "🎉 GPO Local Brain started successfully!"
    echo ""
    echo "📊 Status: docker logs gpo-local-brain"
    echo "🛑 Stop: docker stop gpo-local-brain"
    echo "📂 Documents: Place files in ./documents/ folder"
    echo "🌐 Web UI: http://localhost:8080 (if enabled)"
else
    echo "❌ Failed to start Local Brain"
    echo "Check Docker logs: docker logs gpo-local-brain"
    exit 1
fi 