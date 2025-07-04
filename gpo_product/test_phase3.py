#!/usr/bin/env python3
"""
Test script for Phase 3: Project Request & Blueprint Display
Tests the new project request functionality and API endpoints
"""

import sys
import os
import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app  # type: Flask
from database import db, Project, Organization, User, LinguistProfile
from forms import NewProjectRequestForm

def test_phase3_functionality():
    """Test Phase 3 functionality"""
    print("🧪 Testing Phase 3: Project Request & Blueprint Display")
    print("=" * 60)
    
    with app.app_context():  # type: ignore
        db.create_all()  # Ensure all tables exist
        # Test 1: Check if Project model has new AI fields
        print("\n1. Testing Project Model AI Fields...")
        project = Project()
        
        # Check if new AI fields exist
        ai_fields = [
            'ai_overall_risk_status', 'ai_risk_reason', 'ai_document_complexity',
            'ai_key_challenges', 'ai_sensitive_data_alert_summary',
            'ai_recommended_linguist_profile_text', 'ai_optimal_team_size',
            'ai_deadline_fit_assessment', 'ai_strategic_recommendations',
            'ai_analysis_timestamp', 'local_analysis_status'
        ]
        
        for field in ai_fields:
            if hasattr(project, field):
                print(f"   ✅ {field} field exists")
            else:
                print(f"   ❌ {field} field missing")
                return False, None, None, None
        
        # Test 2: Check if Organization has API key field
        print("\n2. Testing Organization API Key Field...")
        org = Organization()
        if hasattr(org, 'api_key'):
            print("   ✅ api_key field exists")
        else:
            print("   ❌ api_key field missing")
            return False, None, None, None
        
        # Test 3: Test NewProjectRequestForm
        print("\n3. Testing NewProjectRequestForm...")
        with app.test_request_context():  # type: ignore
            form = NewProjectRequestForm()
            required_fields = [
                'project_name', 'client_name', 'source_lang', 'target_lang',
                'desired_deadline', 'content_type_selection', 'selected_linguist_id_for_planning'
            ]
            
            for field in required_fields:
                if hasattr(form, field):
                    print(f"   ✅ {field} field exists")
                else:
                    print(f"   ❌ {field} field missing")
                    return False, None, None, None
        
        # Test 4: Test project creation with new fields
        print("\n4. Testing Project Creation with New Fields...")
        try:
            # Create a test organization
            org = Organization()
            org.id = str(uuid.uuid4())
            org.name = "Test Organization"
            org.api_key = "test_api_key_12345"
            db.session.add(org)
            db.session.commit()
            
            # Create a test user
            user = User()
            user.id = str(uuid.uuid4())
            user.email = "test@example.com"
            user.name = "Test User"
            user.organization_id = org.id
            user.role = "pm"
            user.password_hash = "test_hash"
            db.session.add(user)
            db.session.commit()
            
            # Create a test project with new fields
            project = Project()
            project.id = str(uuid.uuid4())
            project.client_name = "Test Client"
            project.project_name = "Test Project"
            project.source_lang = "EN"
            project.target_lang = "ES"
            project.content_type = "Legal"
            project.desired_deadline = datetime.now().date() + timedelta(days=30)
            project.organization_id = org.id
            project.created_by = user.id
            project.local_analysis_status = 'Pending Local Analysis'
            db.session.add(project)
            db.session.commit()
            
            print("   ✅ Project created successfully with new fields")
            
            # Test 5: Test AI results update
            print("\n5. Testing AI Results Update...")
            project.ai_overall_risk_status = 'High'
            project.ai_risk_reason = 'Complex legal terminology detected'
            project.ai_document_complexity = 'High'
            project.ai_key_challenges = 'Extensive legal jargon, technical terms'
            project.ai_sensitive_data_alert_summary = 'Contains 3 instances of PII in section 2'
            project.ai_recommended_linguist_profile_text = 'Specialist Legal (Patent Law)'
            project.ai_optimal_team_size = '2'
            project.ai_deadline_fit_assessment = 'Deadline is achievable with MTPE'
            project.ai_strategic_recommendations = 'Initiate secure workflow, leverage TM/TB'
            project.ai_analysis_timestamp = datetime.utcnow()
            project.local_analysis_status = 'Analysis Complete'
            db.session.commit()
            
            # Verify the updates
            updated_project = Project.query.get(project.id)
            if updated_project and (updated_project.ai_overall_risk_status == 'High' and 
                updated_project.local_analysis_status == 'Analysis Complete'):
                print("   ✅ AI results updated successfully")
            else:
                print("   ❌ AI results update failed")
                return False, None, None, None
            
        except Exception as e:
            print(f"   ❌ Error during project creation test: {e}")
            return False, None, None, None
        
        print("\n🎉 All Phase 3 tests passed!")
        return org.api_key, org, user, project  # Return the valid API key and objects

def test_api_endpoint(valid_api_key):
    """Test the API endpoint for local analysis results"""
    print("\n6. Testing API Endpoint...")
    
    with app.test_client() as client:  # type: ignore
        # Test with invalid API key
        response = client.post('/api/local-analysis-results', 
                             headers={'X-API-Key': 'invalid_key'},
                             json={'local_analysis_request_id': 'test'})
        
        if response.status_code == 401:
            print("   ✅ API key validation working")
        else:
            print(f"   ❌ API key validation failed: {response.status_code}")
            return False
        
        # Test with missing payload
        response = client.post('/api/local-analysis-results',
                             headers={'X-API-Key': valid_api_key})
        
        if response.status_code == 400:
            print("   ✅ Missing payload validation working")
        else:
            print(f"   ❌ Missing payload validation failed: {response.status_code}")
            return False
    
    print("   ✅ API endpoint tests passed")
    return True

if __name__ == "__main__":
    try:
        valid_api_key, org, user, project = test_phase3_functionality()
        if valid_api_key:
            success = test_api_endpoint(valid_api_key)
        else:
            success = False
        
        # Cleanup after all tests
        with app.app_context():  # type: ignore
            if project:
                db.session.delete(project)
            if user:
                db.session.delete(user)
            if org:
                db.session.delete(org)
            db.session.commit()
        
        if success:
            print("\n✅ Phase 3 implementation is working correctly!")
            sys.exit(0)
        else:
            print("\n❌ Phase 3 implementation has issues!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1) 