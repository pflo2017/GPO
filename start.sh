#!/bin/bash

# GPO Production Startup Script
# This script starts both the GPO web application and the Local Brain component

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       GPO Production Startup Script        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0 # Port is in use
    else
        return 1 # Port is free
    fi
}

# Function to kill process using a specific port
kill_port_process() {
    local port=$1
    local pid=$(lsof -t -i :$port)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}⚠️  Process using port $port (PID: $pid) will be terminated${NC}"
        kill -9 $pid
        sleep 1
        echo -e "${GREEN}✅ Process terminated${NC}"
    fi
}

# Check for Python and required packages
echo -e "${BLUE}🔍 Checking environment...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Check if .env file exists, create if it doesn't
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating default .env file...${NC}"
    cat > .env << EOF
# Database Configuration
SUPABASE_HOST=db.dbbpghthgnwozewmlzes.supabase.co
SUPABASE_PORT=5432
SUPABASE_USER=postgres
SUPABASE_PASSWORD=UCOXZibz5OLgTofg
SUPABASE_DB=postgres

# Application Settings
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(24))")
FLASK_ENV=production
DEBUG=False

# Local Brain Configuration
GPO_CLOUD_API_URL=http://localhost:5001
GPO_ORGANIZATION_API_KEY=local-dev-key
EOF
    echo -e "${GREEN}✅ Created default .env file${NC}"
fi

# Check if ports are in use
GPO_PORT=5001
LOCAL_BRAIN_PORT=5002

echo -e "${BLUE}🔍 Checking if ports are available...${NC}"

if check_port $GPO_PORT; then
    echo -e "${YELLOW}⚠️  Port $GPO_PORT is already in use${NC}"
    read -p "Do you want to kill the process using port $GPO_PORT? (y/n): " kill_process
    if [[ $kill_process == "y" || $kill_process == "Y" ]]; then
        kill_port_process $GPO_PORT
    else
        echo -e "${RED}❌ Cannot start GPO application. Port $GPO_PORT is in use.${NC}"
        exit 1
    fi
fi

if check_port $LOCAL_BRAIN_PORT; then
    echo -e "${YELLOW}⚠️  Port $LOCAL_BRAIN_PORT is already in use${NC}"
    read -p "Do you want to kill the process using port $LOCAL_BRAIN_PORT? (y/n): " kill_process
    if [[ $kill_process == "y" || $kill_process == "Y" ]]; then
        kill_port_process $LOCAL_BRAIN_PORT
    else
        echo -e "${RED}❌ Cannot start Local Brain. Port $LOCAL_BRAIN_PORT is in use.${NC}"
        exit 1
    fi
fi

# Install requirements if needed
echo -e "${BLUE}🔄 Checking dependencies...${NC}"
pip install -r requirements.txt

# Create uploads directory if it doesn't exist
mkdir -p gpo_product/uploads

# Start the GPO application in the background
echo -e "${BLUE}🚀 Starting GPO Web Application...${NC}"
python app.py > gpo_app.log 2>&1 &
GPO_PID=$!
echo -e "${GREEN}✅ GPO Web Application started (PID: $GPO_PID)${NC}"
echo -e "${BLUE}📊 Web interface available at: http://localhost:$GPO_PORT${NC}"

# Wait for GPO app to start
echo -e "${BLUE}⏳ Waiting for GPO Web Application to initialize...${NC}"
sleep 5

# Start the Local Brain in a separate terminal if possible
echo -e "${BLUE}🧠 Starting GPO Local Brain...${NC}"
if command -v osascript &> /dev/null; then
    # On macOS, open a new terminal window
    osascript -e "tell app \"Terminal\" to do script \"cd $(pwd) && source venv/bin/activate && cd gpo_local_brain && python main.py demo-org-id\""
    echo -e "${GREEN}✅ GPO Local Brain started in a new terminal window${NC}"
else
    # On other systems, start in background
    cd gpo_local_brain && python main.py demo-org-id > ../local_brain.log 2>&1 &
    LOCAL_BRAIN_PID=$!
    echo -e "${GREEN}✅ GPO Local Brain started (PID: $LOCAL_BRAIN_PID)${NC}"
    cd ..
fi

echo -e "${GREEN}✅ GPO System is now running${NC}"
echo -e "${BLUE}📝 Logs are available in gpo_app.log and local_brain.log${NC}"
echo -e "${YELLOW}⚠️  Press Ctrl+C to stop the application${NC}"

# Keep the script running to allow Ctrl+C to work
trap "echo -e '${RED}Stopping GPO System...${NC}'; kill $GPO_PID 2>/dev/null; pkill -f 'python.*main.py.*demo-org-id' 2>/dev/null; echo -e '${GREEN}✅ GPO System stopped${NC}'" INT
wait $GPO_PID 