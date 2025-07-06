#!/usr/bin/env python3
"""
GPO - Main Entry Point
This is the main entry point for the GPO application.
It imports and runs the current GPO application from the gpo_product directory.
"""

import sys
import os
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the gpo_product directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
gpo_product_dir = os.path.join(current_dir, 'gpo_product')
sys.path.insert(0, gpo_product_dir)

# Store original directory to restore later
original_dir = os.getcwd()

try:
    # Change to gpo_product directory for relative imports
    os.chdir(gpo_product_dir)
    logger.info(f"Changed working directory to: {gpo_product_dir}")
    
    # Import the current GPO application
    from gpo_product.app import app  # type: Flask
    
    logger.info("🚀 Successfully imported GPO application")
    
    # For local development
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5001))
        debug = os.environ.get('FLASK_ENV', 'development') == 'development'
        
        print("🚀 Starting GPO Application from root directory...")
        print("📱 This will run the full GPO application with all features")
        print(f"🌐 Server will be available at http://localhost:{port}")
        
        app.run(host='0.0.0.0', port=port, debug=debug)
        
except ImportError as e:
    logger.error(f"❌ Error importing GPO application: {e}")
    print(f"❌ Error importing GPO application: {e}")
    print("🔧 Make sure you're in the correct directory and all dependencies are installed")
    import traceback
    traceback.print_exc()
    
    # Try alternative import
    try:
        logger.info("Attempting alternative import...")
        from gpo_product.app import app as gpo_app
        app = gpo_app
        logger.info("✅ Alternative import successful")
    except Exception as e:
        logger.error(f"❌ Alternative import failed: {e}")
        # Restore original directory before exiting
        os.chdir(original_dir)
        sys.exit(1)
except Exception as e:
    logger.error(f"❌ Unexpected error: {e}")
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    
    # Restore original directory before exiting
    os.chdir(original_dir)
    sys.exit(1)
finally:
    # Restore original directory
    os.chdir(original_dir)