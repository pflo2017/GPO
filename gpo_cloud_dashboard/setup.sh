#!/bin/bash

# Exit on error
set -e

echo "Setting up GPO Central Intelligence Dashboard..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p instance

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp example.env .env
    echo "Please update the .env file with your credentials."
fi

# Initialize database
echo "Initializing database..."
export FLASK_APP=app.py
flask shell << EOF
from app import create_app
from models import db
app = create_app('development')
with app.app_context():
    db.create_all()
EOF

echo "Setup complete!"
echo "Run the application with: python run.py" 