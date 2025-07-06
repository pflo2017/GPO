#!/usr/bin/env python3
"""
GPO Comprehensive Test Script
This script sets up a complete test environment with real documents and triggers actual AI analysis.
"""

import os
import sys
import uuid
import time
import json
import random
import requests
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import shutil

# Load environment variables
load_dotenv()

# Initialize faker
fake = Faker()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_HOST', 'db.dbbpghthgnwozewmlzes.supabase.co')
DB_PORT = os.getenv('SUPABASE_PORT', '5432')
DB_USER = os.getenv('SUPABASE_USER', 'postgres')
DB_PASSWORD = os.getenv('SUPABASE_PASSWORD', 'UCOXZibz5OLgTofg')
DB_NAME = os.getenv('SUPABASE_DB', 'postgres')

# GPO API settings
GPO_API_URL = os.getenv('GPO_CLOUD_API_URL', 'http://localhost:5001')
API_KEY = os.getenv('GPO_ORGANIZATION_API_KEY', 'local-dev-key')

# Path to sample documents
SAMPLE_DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dummy_docs')
if not os.path.exists(SAMPLE_DOCS_DIR):
    SAMPLE_DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dummy_docs')

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Connect to database
def connect_to_db():
    try:
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)
        conn = engine.connect()
        print("✅ Connected to database")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

# Create test organization
def create_test_organization(conn):
    org_id = str(uuid.uuid4())
    org_name = f"{fake.company()} Translations"
    api_key = str(uuid.uuid4())
    
    try:
        conn.execute(text("""
        INSERT INTO organizations (id, name, subscription_tier, api_key, created_at, updated_at)
        VALUES (:id, :name, 'professional', :api_key, NOW(), NOW())
        """), {"id": org_id, "name": org_name, "api_key": api_key})
        
        print(f"✅ Created test organization: {org_name} (ID: {org_id})")
        return org_id, org_name, api_key
    except Exception as e:
        print(f"❌ Failed to create organization: {e}")
        # Check if organization already exists
        result = conn.execute(text("SELECT id, name, api_key FROM organizations LIMIT 1")).fetchone()
        if result:
            print(f"✅ Using existing organization: {result[1]} (ID: {result[0]})")
            return result[0], result[1], result[2]
        sys.exit(1)

# Create test admin user
def create_test_user(conn, org_id):
    user_id = str(uuid.uuid4())
    email = "admin@test.com"
    name = "Test Admin"
    # This is a hashed version of "password"
    password_hash = "$2b$12$Q5C4Eb8mMCVt9Nz26kxDZOmppDHROlWV5z.9pRnUY3XiCw4Qn8JLe"
    
    try:
        # Check if user already exists
        existing_user = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email}).fetchone()
        if existing_user:
            print(f"✅ Using existing admin user: {email}")
            return existing_user[0]
            
        conn.execute(text("""
        INSERT INTO users (id, email, name, password_hash, role, organization_id, created_at, updated_at)
        VALUES (:id, :email, :name, :password_hash, 'admin', :org_id, NOW(), NOW())
        """), {"id": user_id, "email": email, "name": name, "password_hash": password_hash, "org_id": org_id})
        
        print(f"✅ Created admin user: {email} (ID: {user_id})")
        return user_id
    except Exception as e:
        print(f"❌ Failed to create user: {e}")
        sys.exit(1)

# Create test linguist profiles
def create_test_linguists(conn, org_id, count=5):
    linguist_ids = []
    
    # Check if linguists already exist
    existing_count = conn.execute(text(
        "SELECT COUNT(*) FROM linguist_profiles WHERE organization_id = :org_id"
    ), {"org_id": org_id}).fetchone()[0]
    
    if existing_count >= count:
        print(f"✅ Using {existing_count} existing linguist profiles")
        linguist_ids = [row[0] for row in conn.execute(text(
            "SELECT id FROM linguist_profiles WHERE organization_id = :org_id LIMIT :limit"
        ), {"org_id": org_id, "limit": count}).fetchall()]
        return linguist_ids
    
    languages = ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Russian", "Arabic", "Portuguese"]
    specializations = ["Legal", "Medical", "Technical", "Marketing", "Financial", "Literary", "IT", "Scientific"]
    
    for i in range(count):
        linguist_id = str(uuid.uuid4())
        internal_id = f"L{1000 + i}"
        full_name = fake.name()
        email = fake.email()
        source_langs = ", ".join(random.sample(languages, 2))
        target_langs = ", ".join(random.sample([l for l in languages if l not in source_langs], 2))
        specializations_list = ", ".join(random.sample(specializations, 3))
        quality_rating = random.choice(["A", "A+", "B+", "A-"])
        capacity = random.randint(2000, 5000)
        
        try:
            conn.execute(text("""
            INSERT INTO linguist_profiles (id, organization_id, internal_id, full_name, email, 
                                          specializations, source_languages, target_languages, 
                                          quality_rating, general_capacity_words_per_day, status)
            VALUES (:id, :org_id, :internal_id, :full_name, :email, :specializations, 
                   :source_langs, :target_langs, :quality_rating, :capacity, 'Active')
            """), {
                "id": linguist_id, "org_id": org_id, "internal_id": internal_id,
                "full_name": full_name, "email": email, "specializations": specializations_list,
                "source_langs": source_langs, "target_langs": target_langs,
                "quality_rating": quality_rating, "capacity": capacity
            })
            
            linguist_ids.append(linguist_id)
        except Exception as e:
            print(f"❌ Failed to create linguist {i+1}: {e}")
    
    print(f"✅ Created {len(linguist_ids)} linguist profiles")
    return linguist_ids

# Create test project with real documents
def create_test_project(conn, org_id, user_id, linguist_ids):
    project_id = str(uuid.uuid4())
    project_name = f"Test Project {datetime.now().strftime('%Y%m%d-%H%M%S')}"
    client_name = fake.company()
    source_lang = "English"
    target_lang = "Spanish"
    content_type = random.choice(["Legal", "Medical", "Technical", "Marketing"])
    deadline = (datetime.now() + timedelta(days=random.randint(5, 30))).date()
    
    try:
        conn.execute(text("""
        INSERT INTO projects (id, client_name, project_name, source_lang, target_lang, 
                            content_type, desired_deadline, organization_id, created_by, 
                            created_at, updated_at, status, local_analysis_status)
        VALUES (:id, :client_name, :project_name, :source_lang, :target_lang, 
               :content_type, :deadline, :org_id, :user_id, NOW(), NOW(), 
               'New', 'Pending Local Analysis')
        """), {
            "id": project_id, "client_name": client_name, "project_name": project_name,
            "source_lang": source_lang, "target_lang": target_lang, "content_type": content_type,
            "deadline": deadline, "org_id": org_id, "user_id": user_id
        })
        
        print(f"✅ Created test project: {project_name} (ID: {project_id})")
        return project_id, project_name, content_type
    except Exception as e:
        print(f"❌ Failed to create project: {e}")
        sys.exit(1)

# Copy and attach sample documents to the project
def attach_documents(conn, project_id, content_type):
    document_ids = []
    
    # Get sample documents based on content type
    sample_docs = []
    for filename in os.listdir(SAMPLE_DOCS_DIR):
        if filename.endswith(('.txt', '.docx', '.pdf')):
            sample_docs.append(filename)
    
    if not sample_docs:
        print("❌ No sample documents found. Creating dummy text files...")
        # Create dummy text files if no samples are available
        os.makedirs(SAMPLE_DOCS_DIR, exist_ok=True)
        for i in range(3):
            dummy_content = f"This is a sample {content_type.lower()} document for testing.\n\n"
            dummy_content += "\n".join([fake.paragraph() for _ in range(10)])
            
            filename = f"sample_{content_type.lower()}_{i+1}.txt"
            filepath = os.path.join(SAMPLE_DOCS_DIR, filename)
            with open(filepath, 'w') as f:
                f.write(dummy_content)
            sample_docs.append(filename)
    
    # Copy and attach documents
    for i, filename in enumerate(sample_docs[:3]):  # Limit to 3 documents
        source_path = os.path.join(SAMPLE_DOCS_DIR, filename)
        file_ext = os.path.splitext(filename)[1]
        new_filename = f"{project_id}_{i+1}{file_ext}"
        dest_path = os.path.join(UPLOAD_DIR, new_filename)
        
        # Copy file to uploads directory
        shutil.copy2(source_path, dest_path)
        
        # Calculate word count (simplified)
        word_count = 0
        try:
            with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                word_count = len(content.split())
        except:
            word_count = random.randint(500, 3000)
        
        # Add document to database
        try:
            result = conn.execute(text("""
            INSERT INTO project_documents (project_id, file_name, file_path, file_type, word_count, status, created_at, updated_at)
            VALUES (:project_id, :file_name, :file_path, :file_type, :word_count, 'Uploaded', NOW(), NOW())
            RETURNING id
            """), {
                "project_id": project_id, "file_name": filename, 
                "file_path": dest_path, "file_type": file_ext[1:],
                "word_count": word_count
            })
            
            doc_id = result.fetchone()[0]
            document_ids.append(doc_id)
            print(f"✅ Attached document: {filename} (ID: {doc_id}, Words: {word_count})")
        except Exception as e:
            print(f"❌ Failed to attach document {filename}: {e}")
    
    return document_ids

# Trigger local brain analysis
def trigger_analysis(project_id, api_key):
    try:
        # Check if Local Brain is running
        try:
            response = requests.get(f"{GPO_API_URL}/api/health", timeout=2)
            if response.status_code != 200:
                print("⚠️ GPO API not responding. Make sure the application is running.")
        except:
            print("⚠️ GPO API not responding. Make sure the application is running.")
        
        # Trigger analysis via API
        headers = {"X-API-Key": api_key}
        payload = {"project_id": project_id, "force_reanalysis": True}
        
        print(f"🔄 Triggering AI analysis for project {project_id}...")
        response = requests.post(f"{GPO_API_URL}/api/analyze-project", json=payload, headers=headers)
        
        if response.status_code == 200:
            print("✅ Analysis request sent successfully")
            print("⏳ Analysis is now running in the Local Brain component")
            print("🔍 You can check the status in the web interface")
        else:
            print(f"❌ Failed to trigger analysis: {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Failed to trigger analysis: {e}")

# Main function
def main():
    print("🚀 Starting GPO Comprehensive Test")
    print("==================================")
    
    # Connect to database
    conn = connect_to_db()
    
    try:
        # Create test data
        org_id, org_name, api_key = create_test_organization(conn)
        user_id = create_test_user(conn, org_id)
        linguist_ids = create_test_linguists(conn, org_id)
        
        # Create project with documents
        project_id, project_name, content_type = create_test_project(conn, org_id, user_id, linguist_ids)
        document_ids = attach_documents(conn, project_id, content_type)
        
        # Commit all changes
        conn.execute(text("COMMIT"))
        
        print("\n📊 Test Environment Summary")
        print("==========================")
        print(f"Organization: {org_name}")
        print(f"Admin User: admin@test.com (password: password)")
        print(f"Project: {project_name}")
        print(f"Documents: {len(document_ids)} attached")
        
        # Trigger analysis
        print("\n🧠 Starting AI Analysis")
        print("=====================")
        trigger_analysis(project_id, api_key)
        
        print("\n✅ Test setup complete!")
        print("📱 You can now log in to the web interface with:")
        print("   Email: admin@test.com")
        print("   Password: password")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main() 