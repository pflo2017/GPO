#!/usr/bin/env python3
"""
Database fix script for GPO
This script ensures all tables are created with the correct schema
"""

import os
import sys
from dotenv import load_dotenv
import json
import uuid
from werkzeug.security import generate_password_hash

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from flask import Flask
from database import db, init_database, Organization, User, Linguist, Project, ProjectDocument, AuditLog, Notification, LinguistProfile, PasswordReset

def create_app():
    """Create a minimal Flask app for database operations"""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-testing')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    init_database(app)
    
    return app

def main():
    """Main function to fix database"""
    print("🔧 Fixing GPO Database...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check existing tables
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"📋 Found existing tables: {', '.join(existing_tables)}")
            
            # Drop all tables that reference organizations, then drop organizations
            drop_order = [
                'project_documents',
                'projects',
                'linguists',
                'linguist_profiles',
                'audit_logs',
                'notifications',
                'password_resets',
                'users',
                'organizations'
            ]
            for table in drop_order:
                if table in existing_tables:
                    print(f"🔄 Dropping table {table} to fix schema...")
                    db.session.execute(db.text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    db.session.commit()
                    print(f"✅ Dropped table {table}")
            
            # Create all tables with correct schema
            print("🔄 Creating all tables with correct schema...")
            db.create_all()
            print("✅ All tables created successfully")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"📋 Final tables: {', '.join(existing_tables)}")
            
            # Check if we need to create a default organization and admin user
            if not Organization.query.first():
                print("🔄 Creating default organization...")
                default_org = Organization()
                default_org.id = str(uuid.uuid4())
                default_org.name = "Default Organization"
                default_org.subscription_tier = "free"
                default_org.subscription_status = "active"
                default_org.max_users = 10
                default_org.max_projects = 50
                default_org.max_storage_gb = 10
                default_org.features_enabled = json.dumps(["basic_features"])
                
                db.session.add(default_org)
                db.session.commit()
                print("✅ Default organization created")
                
                # Create admin user
                print("🔄 Creating admin user...")
                admin_user = User()
                admin_user.id = str(uuid.uuid4())
                admin_user.email = "admin@gpo.com"
                admin_user.name = "Admin User"
                admin_user.password_hash = generate_password_hash("admin123")
                admin_user.role = "admin"
                admin_user.organization_id = default_org.id
                
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin user created (email: admin@gpo.com, password: admin123)")
            
            print("🎉 Database fix completed successfully!")
            
        except Exception as e:
            print(f"❌ Error fixing database: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 