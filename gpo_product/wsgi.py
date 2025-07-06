#!/usr/bin/env python3
"""
WSGI Entry Point for GPO Application
This file serves as the entry point for WSGI servers like Gunicorn.
"""

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the Flask app
from app import app

# For direct execution
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 