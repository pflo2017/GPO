#!/usr/bin/env python3
"""
Deployment Test Script for GPO
This script tests if the GPO application can start properly in a deployment environment.
"""

import os
import sys
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from flask import Flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    try:
        from flask_sqlalchemy import SQLAlchemy
        print("✅ Flask-SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ Flask-SQLAlchemy import failed: {e}")
        return False
    
    try:
        from flask_login import LoginManager
        print("✅ Flask-Login imported successfully")
    except ImportError as e:
        print(f"❌ Flask-Login import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test if the Flask app can be created"""
    print("\n🔍 Testing app creation...")
    
    try:
        from app import app
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from app import app
        with app.app_context():
            from database import db
            db.engine.connect()
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        traceback.print_exc()
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    required_vars = [
        'SUPABASE_HOST',
        'SUPABASE_DB', 
        'SUPABASE_USER',
        'SUPABASE_PASSWORD',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def main():
    """Run all deployment tests"""
    print("🚀 GPO Deployment Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        sys.exit(1)
    
    # Test environment
    if not test_environment():
        print("\n❌ Environment tests failed")
        sys.exit(1)
    
    # Test app creation
    if not test_app_creation():
        print("\n❌ App creation tests failed")
        sys.exit(1)
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection tests failed")
        sys.exit(1)
    
    print("\n✅ All deployment tests passed!")
    print("🎉 GPO is ready for deployment")

if __name__ == '__main__':
    main() 