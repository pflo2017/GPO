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

# Add parent directory to path for .env file
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Load environment variables (don't fail if .env doesn't exist)
try:
    from dotenv import load_dotenv
    # Try to load from parent directory first, then current directory
    env_loaded = load_dotenv(os.path.join(parent_dir, '.env')) or load_dotenv('.env')
    if not env_loaded:
        print("Warning: No .env file found, using environment variables")
except ImportError:
    print("Warning: python-dotenv not available, using environment variables")

# Set default environment variables for production
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('SECRET_KEY', 'default-secret-key-change-in-production')

# Import the Flask app
try:
    from app import app
    print("✅ Successfully imported Flask app")
except ImportError as e:
    print(f"❌ Error importing Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# For direct execution
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 