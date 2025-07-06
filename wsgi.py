#!/usr/bin/env python3
"""
Root WSGI Entry Point for GPO Application
This file serves as an alternative entry point for WSGI servers.
"""

import os
import sys

# Add the gpo_product directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
gpo_product_dir = os.path.join(current_dir, 'gpo_product')
sys.path.insert(0, gpo_product_dir)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not available")

# Set default environment variables for production
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('SECRET_KEY', 'default-secret-key-change-in-production')

# Import the Flask app from gpo_product
try:
    from app import app
    print("✅ Successfully imported Flask app from gpo_product")
except ImportError as e:
    print(f"❌ Error importing Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# For direct execution
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 