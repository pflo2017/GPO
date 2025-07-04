#!/usr/bin/env python3
"""
GPO - Main Entry Point
This is the main entry point for the GPO application.
It imports and runs the current GPO application from the gpo_product directory.
"""

import sys
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask

# Add the gpo_product directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
gpo_product_dir = os.path.join(current_dir, 'gpo_product')
sys.path.insert(0, gpo_product_dir)

# Change to gpo_product directory for relative imports
os.chdir(gpo_product_dir)

# Import the current GPO application
try:
    from app import app  # type: Flask
    print("🚀 Starting GPO Application from root directory...")
    print("📱 This will run the full GPO application with all features")
    print("🌐 Server will be available at http://localhost:5001")
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5001, debug=True)  # type: ignore
        
except ImportError as e:
    print(f"❌ Error importing GPO application: {e}")
    print("🔧 Make sure you're in the correct directory and all dependencies are installed")
    import traceback
    traceback.print_exc()
    sys.exit(1)