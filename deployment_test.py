#!/usr/bin/env python3
"""
Deployment Test Script for GPO

This script tests the deployment configuration and environment
to help identify and fix issues before deploying to production.
"""

import os
import sys
import importlib
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """Check the environment variables and Python version."""
    logger.info("Checking environment...")
    
    # Check Python version
    python_version = sys.version
    logger.info(f"Python version: {python_version}")
    
    # Check key environment variables
    env_vars = [
        'FLASK_ENV',
        'SECRET_KEY',
        'SUPABASE_HOST',
        'SUPABASE_DB',
        'SUPABASE_USER',
        'SUPABASE_PASSWORD',
        'SUPABASE_PORT',
        'PORT'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if var in ['SECRET_KEY', 'SUPABASE_PASSWORD']:
                logger.info(f"{var}: ***MASKED***")
            else:
                logger.info(f"{var}: {value}")
        else:
            logger.warning(f"{var}: Not set")
    
    return True

def check_imports():
    """Check if all required modules can be imported."""
    logger.info("Checking imports...")
    
    required_modules = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_wtf',
        'sqlalchemy',
        'psycopg2',
        'dotenv',
        'gunicorn'
    ]
    
    all_passed = True
    for module in required_modules:
        try:
            importlib.import_module(module)
            logger.info(f"✅ {module}: Successfully imported")
        except ImportError as e:
            logger.error(f"❌ {module}: Import failed - {str(e)}")
            all_passed = False
    
    return all_passed

def check_application():
    """Check if the application can be imported and initialized."""
    logger.info("Checking application...")
    
    try:
        # Add the gpo_product directory to the Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        gpo_product_dir = os.path.join(current_dir, 'gpo_product')
        sys.path.insert(0, gpo_product_dir)
        
        # Store original directory
        original_dir = os.getcwd()
        
        try:
            # Change to gpo_product directory for relative imports
            os.chdir(gpo_product_dir)
            logger.info(f"Changed working directory to: {gpo_product_dir}")
            
            # Try to import the app
            from gpo_product.app import app
            logger.info("✅ Application imported successfully")
            
            # Check if app is a Flask application
            if hasattr(app, 'route'):
                logger.info("✅ Application is a valid Flask application")
            else:
                logger.error("❌ Application does not appear to be a valid Flask application")
                return False
                
            # Check database configuration
            if hasattr(app, 'config'):
                if 'SQLALCHEMY_DATABASE_URI' in app.config:
                    # Mask the actual URI
                    logger.info("✅ Database URI is configured")
                else:
                    logger.warning("⚠️ Database URI not found in app configuration")
            
            return True
            
        finally:
            # Restore original directory
            os.chdir(original_dir)
            
    except Exception as e:
        logger.error(f"❌ Application check failed: {str(e)}")
        traceback.print_exc()
        return False

def check_database_connection():
    """Check if the database connection works."""
    logger.info("Checking database connection...")
    
    try:
        # Add the gpo_product directory to the Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        gpo_product_dir = os.path.join(current_dir, 'gpo_product')
        sys.path.insert(0, gpo_product_dir)
        
        # Store original directory
        original_dir = os.getcwd()
        
        try:
            # Change to gpo_product directory for relative imports
            os.chdir(gpo_product_dir)
            
            # Try to import the database module
            from database import db, init_database
            from flask import Flask
            
            # Create a test app
            test_app = Flask(__name__)
            test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            
            # Initialize the database with the test app
            init_database(test_app)
            
            # Test the connection
            with test_app.app_context():
                db.engine.connect()
                logger.info("✅ Database connection successful")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            traceback.print_exc()
            return False
            
        finally:
            # Restore original directory
            os.chdir(original_dir)
            
    except Exception as e:
        logger.error(f"❌ Database check failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all checks and report results."""
    logger.info("Starting deployment tests...")
    
    results = {
        "Environment": check_environment(),
        "Imports": check_imports(),
        "Application": check_application(),
        "Database": check_database_connection()
    }
    
    logger.info("\n=== Test Results ===")
    all_passed = True
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 All tests passed! The application should deploy successfully.")
        return 0
    else:
        logger.error("\n⚠️ Some tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 