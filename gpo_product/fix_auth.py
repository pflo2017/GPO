#!/usr/bin/env python3
"""
Fix Authentication Issues
This script fixes users with empty password hashes and other auth issues.
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not available")

from database import db, User, init_database
from app import app

def fix_empty_password_hashes():
    """Fix users with empty password hashes"""
    with app.app_context():
        # Database is already initialized in app
        
        # Find users with empty password hashes
        users_with_empty_hash = User.query.filter(
            (User.password_hash == '') | 
            (User.password_hash.is_(None))
        ).all()
        
        print(f"Found {len(users_with_empty_hash)} users with empty password hashes")
        
        for user in users_with_empty_hash:
            print(f"Fixing user: {user.email}")
            # Set a default password hash (user will need to reset password)
            user.password_hash = generate_password_hash('changeme123')
        
        if users_with_empty_hash:
            db.session.commit()
            print("✅ Fixed empty password hashes")
            print("⚠️  Users will need to reset their passwords")
        else:
            print("✅ No users with empty password hashes found")

def create_default_admin():
    """Create a default admin user if none exists"""
    with app.app_context():
        # Database is already initialized in app
        
        # Check if any admin users exist
        admin_users = User.query.filter_by(role='admin').all()
        
        if not admin_users:
            print("No admin users found. Creating default admin...")
            
            from auth import Organization
            import uuid
            from datetime import datetime
            
            # Create organization
            org_id = str(uuid.uuid4())
            organization = Organization(
                id=org_id,
                name="Default Organization",
                subscription_tier='free',
                subscription_status='active',
                max_users=5,
                max_projects=10,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(organization)
            
            # Create admin user
            admin_id = str(uuid.uuid4())
            admin_user = User(
                id=admin_id,
                email='admin@gpo.com',
                name='Admin User',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                organization_id=org_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(admin_user)
            
            db.session.commit()
            print("✅ Created default admin user:")
            print("   Email: admin@gpo.com")
            print("   Password: admin123")
        else:
            print(f"✅ Found {len(admin_users)} admin users")

if __name__ == '__main__':
    print("🔧 Fixing authentication issues...")
    fix_empty_password_hashes()
    create_default_admin()
    print("✅ Authentication fixes completed!") 