#!/bin/bash

# GPO Demo Script
# This script sets up and runs a complete GPO demo with real AI analysis

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 Starting GPO Demo Setup${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if any GPO processes are already running
echo -e "${YELLOW}Checking for existing GPO processes...${NC}"
pkill -f "python app.py" || true
pkill -f "python gpo_local_brain/main.py" || true
sleep 2

# Create necessary directories
echo -e "${YELLOW}Setting up directories...${NC}"
mkdir -p gpo_local_brain/documents
mkdir -p gpo_local_brain/processed
mkdir -p gpo_product/uploads

# Copy sample documents to dummy_docs if they don't exist
if [ ! -f dummy_docs/sample_legal_contract.txt ]; then
    echo -e "${YELLOW}Creating sample documents...${NC}"
    cp -n gpo_product/sample_documents/* dummy_docs/ 2>/dev/null || true
fi

# Run the comprehensive test to set up the database
echo -e "${YELLOW}Setting up test environment...${NC}"
cd gpo_product
python run_comprehensive_test.py
cd ..

# Start the main application in the background
echo -e "${YELLOW}Starting GPO main application...${NC}"
python app.py > gpo_app.log 2>&1 &
APP_PID=$!

# Wait for the application to start
echo -e "${YELLOW}Waiting for application to start...${NC}"
sleep 5

# Start the local brain in the background
echo -e "${YELLOW}Starting GPO Local Brain...${NC}"
cd gpo_local_brain
python main.py > ../local_brain.log 2>&1 &
BRAIN_PID=$!
cd ..

# Wait for the local brain to start
sleep 3

echo -e "${GREEN}✅ Demo environment is ready!${NC}"
echo -e "${GREEN}✅ GPO Application running at: http://localhost:5001${NC}"
echo -e "${GREEN}✅ Login with: admin@test.com / password${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}Demo Instructions:${NC}"
echo -e "1. Open your browser to http://localhost:5001"
echo -e "2. Log in with the credentials above"
echo -e "3. Create a new project from the dashboard"
echo -e "4. To trigger AI analysis, run:"
echo -e "   ${BLUE}cp dummy_docs/sample_legal_contract.txt gpo_local_brain/documents/${NC}"
echo -e "5. Wait a few seconds and refresh the project page to see the analysis"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the demo when finished${NC}"

# Wait for Ctrl+C
trap "echo -e '${RED}Stopping GPO Demo...${NC}'; kill $APP_PID $BRAIN_PID; exit" INT
wait 