#!/bin/bash

# GPO Product Setup Script
# This script sets up the GPO product environment and fixes common issues

echo "🚀 Setting up GPO Product environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}Error: This script must be run from the gpo_product directory${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
echo -e "${BLUE}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate || source venv/Scripts/activate

# Install requirements
echo -e "${BLUE}Installing required packages...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Check if Flask-Login is installed, if not install it
if ! pip list | grep -q "Flask-Login"; then
    echo -e "${YELLOW}⚠️ Flask-Login not found, installing...${NC}"
    pip install Flask-Login
    # Add to requirements.txt if not there
    if ! grep -q "Flask-Login" requirements.txt; then
        echo "Flask-Login" >> requirements.txt
    fi
fi

# Check if PyMuPDF is installed, if not install it
if ! pip list | grep -q "PyMuPDF"; then
    echo -e "${YELLOW}⚠️ PyMuPDF not found, installing...${NC}"
    pip install PyMuPDF
    # Add to requirements.txt if not there
    if ! grep -q "PyMuPDF" requirements.txt; then
        echo "PyMuPDF" >> requirements.txt
    fi
fi

# Check if python-docx is installed, if not install it
if ! pip list | grep -q "python-docx"; then
    echo -e "${YELLOW}⚠️ python-docx not found, installing...${NC}"
    pip install python-docx
    # Add to requirements.txt if not there
    if ! grep -q "python-docx" requirements.txt; then
        echo "python-docx" >> requirements.txt
    fi
fi

# Check if google-generativeai is installed, if not install it
if ! pip list | grep -q "google-generativeai"; then
    echo -e "${YELLOW}⚠️ google-generativeai not found, installing...${NC}"
    pip install google-generativeai
    # Add to requirements.txt if not there
    if ! grep -q "google-generativeai" requirements.txt; then
        echo "google-generativeai" >> requirements.txt
    fi
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file...${NC}"
    cat > .env << EOF
# Database Configuration
SUPABASE_URL=https://dbbpghthgnwozewmlzes.supabase.co
SUPABASE_PASSWORD=UCOXZibz5OLgTofg
SUPABASE_HOST=db.dbbpghthgnwozewmlzes.supabase.co
SUPABASE_PORT=6543
SUPABASE_DB=postgres
SUPABASE_USER=postgres

# Application Configuration
SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRiYnBnaHRoZ253b3pld21semVzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDkzMzg5NCwiZXhwIjoyMDY2NTA5ODk0fQ.8EkU0AD3jTmBVPhdvAj_cVagLE15rV-vML5Ow0mqWuE
FLASK_ENV=development

# AI Configuration
LLM_API_KEY=AIzaSyDvFgJDn3oipZHJFcs5EBD7nU8yjwir_gU
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${YELLOW}⚠️ .env file already exists${NC}"
fi

# Create uploads directory if it doesn't exist
if [ ! -d "uploads" ]; then
    echo -e "${BLUE}Creating uploads directory...${NC}"
    mkdir -p uploads
    echo -e "${GREEN}✅ Uploads directory created${NC}"
else
    echo -e "${YELLOW}⚠️ Uploads directory already exists${NC}"
fi

# Initialize the database
echo -e "${BLUE}Initializing database...${NC}"
python init_db.py

echo -e "${GREEN}✅ Setup complete! You can now run the application with:${NC}"
echo -e "${BLUE}python app.py${NC}" 