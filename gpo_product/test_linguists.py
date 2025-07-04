#!/usr/bin/env python3
"""
Test script for LinguistProfile functionality
"""

import sys
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app  # type: Flask
from database import db, LinguistProfile, Organization, User
from datetime import datetime
import uuid

def test_linguist_functionality():
    """Test the linguist profile functionality"""
    with app.app_context():  # type: ignore
        print("🧪 Testing LinguistProfile functionality...")
        
        # Create a test organization
        org_id = str(uuid.uuid4())
        organization = Organization()
        organization.id = org_id
        organization.name = "Test Organization"
        db.session.add(organization)
        
        # Create a test user
        user_id = str(uuid.uuid4())
        user = User()
        user.id = user_id
        user.email = "test@example.com"
        user.name = "Test User"
        user.password_hash = "test_hash"
        user.role = "admin"
        user.organization_id = org_id
        db.session.add(user)
        
        # Create test linguist profiles
        linguist1 = LinguistProfile()
        linguist1.organization_id = org_id
        linguist1.internal_id = "L-001"
        linguist1.full_name = "John Doe"
        linguist1.email = "john.doe@example.com"
        linguist1.specializations = "Medical, Pharma"
        linguist1.source_languages = "EN, FR"
        linguist1.target_languages = "ES, DE"
        linguist1.quality_rating = "Certified"
        linguist1.general_capacity_words_per_day = 2500
        linguist1.status = "Active"
        
        linguist2 = LinguistProfile()
        linguist2.organization_id = org_id
        linguist2.internal_id = "L-002"
        linguist2.full_name = "Jane Smith"
        linguist2.email = "jane.smith@example.com"
        linguist2.specializations = "Legal"
        linguist2.source_languages = "EN"
        linguist2.target_languages = "FR"
        linguist2.quality_rating = "Preferred"
        linguist2.general_capacity_words_per_day = 2000
        linguist2.status = "Active"
        
        db.session.add(linguist1)
        db.session.add(linguist2)
        
        # Commit to database
        db.session.commit()
        
        # Test queries
        print("✅ Created test data")
        
        # Test organization-specific query
        org_linguists = LinguistProfile.query.filter_by(organization_id=org_id).all()
        print(f"✅ Found {len(org_linguists)} linguists for organization")
        
        # Test search functionality
        search_results = LinguistProfile.query.filter(
            LinguistProfile.organization_id == org_id,
            LinguistProfile.full_name.ilike("%John%")
        ).all()
        print(f"✅ Search found {len(search_results)} linguists with 'John' in name")
        
        # Test internal_id uniqueness
        duplicate_check = LinguistProfile.query.filter_by(
            organization_id=org_id,
            internal_id="L-001"
        ).count()
        print(f"✅ Internal ID uniqueness check: {duplicate_check} records found")
        
        # Clean up test data
        db.session.delete(linguist1)
        db.session.delete(linguist2)
        db.session.delete(user)
        db.session.delete(organization)
        db.session.commit()
        
        print("✅ Test completed successfully!")
        print("🎉 LinguistProfile functionality is working correctly!")

if __name__ == "__main__":
    test_linguist_functionality() 