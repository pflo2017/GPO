#!/usr/bin/env python3
"""
Simple GPO Test Scenario
This script creates a basic test scenario with sample data
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database import User, Organization, Project, ProjectDocument, Linguist
from auth import init_auth

def create_sample_data():
    """Create sample data for testing"""
    
    print("🚀 Creating Sample GPO Data")
    print("=" * 40)
    
    with app.app_context():
        # Create organization
        print("📋 Creating organization...")
        org = Organization(
            id=str(uuid.uuid4()),
            name="GPO Test Organization",
            subscription_tier="premium",
            max_users=50,
            max_projects=100
        )
        db.session.add(org)
        db.session.commit()
        print(f"✅ Organization created: {org.name}")
        
        # Create admin user
        print("👤 Creating admin user...")
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@gpo.com",
            name="Admin User",
            role="admin",
            organization_id=org.id
        )
        admin_user.password_hash = generate_password_hash("admin123")
        db.session.add(admin_user)
        db.session.commit()
        print(f"✅ Admin user created: {admin_user.email}")
        
        # Create manager user
        print("👤 Creating manager user...")
        manager_user = User(
            id=str(uuid.uuid4()),
            email="manager@gpo.com",
            name="Project Manager",
            role="project_manager",
            organization_id=org.id
        )
        manager_user.password_hash = generate_password_hash("manager123")
        db.session.add(manager_user)
        db.session.commit()
        print(f"✅ Manager user created: {manager_user.email}")
        
        # Create client user
        print("👤 Creating client user...")
        client_user = User(
            id=str(uuid.uuid4()),
            email="client@gpo.com",
            name="Test Client",
            role="client",
            organization_id=org.id
        )
        client_user.password_hash = generate_password_hash("client123")
        db.session.add(client_user)
        db.session.commit()
        print(f"✅ Client user created: {client_user.email}")
        
        # Create linguists
        print("🎓 Creating linguists...")
        linguists_data = [
            {
                "name": "Dr. Maria Rodriguez",
                "languages": "en,es,fr",
                "specialties": "medical,legal,technical",
                "speed_score": 85,
                "quality_score": 95,
                "current_load": "Available"
            },
            {
                "name": "Jean-Pierre Dubois",
                "languages": "en,fr,de",
                "specialties": "financial,technical,software",
                "speed_score": 80,
                "quality_score": 92,
                "current_load": "Available"
            },
            {
                "name": "Hans Mueller",
                "languages": "en,de,it",
                "specialties": "engineering,automotive,technical",
                "speed_score": 88,
                "quality_score": 94,
                "current_load": "Available"
            }
        ]
        
        created_linguists = []
        for linguist_data in linguists_data:
            linguist = Linguist(
                name=linguist_data["name"],
                languages=linguist_data["languages"],
                specialties=linguist_data["specialties"],
                speed_score=linguist_data["speed_score"],
                quality_score=linguist_data["quality_score"],
                current_load=linguist_data["current_load"],
                organization_id=org.id
            )
            db.session.add(linguist)
            created_linguists.append(linguist)
        
        db.session.commit()
        print(f"✅ Created {len(created_linguists)} linguists")
        
        # Create projects
        print("📁 Creating projects...")
        projects_data = [
            {
                "client_name": "MedTech Solutions Inc.",
                "project_name": "Medical Device Documentation Translation",
                "source_lang": "en",
                "target_lang": "es,fr,de",
                "content_type": "medical",
                "desired_deadline": datetime.now() + timedelta(days=30)
            },
            {
                "client_name": "Global Retail Corp",
                "project_name": "E-commerce Platform Localization",
                "source_lang": "en",
                "target_lang": "es,fr,de,it",
                "content_type": "software",
                "desired_deadline": datetime.now() + timedelta(days=45)
            },
            {
                "client_name": "International Law Firm",
                "project_name": "Legal Contract Translation",
                "source_lang": "en",
                "target_lang": "es,fr",
                "content_type": "legal",
                "desired_deadline": datetime.now() + timedelta(days=21)
            }
        ]
        
        created_projects = []
        for project_data in projects_data:
            project = Project(
                id=str(uuid.uuid4()),
                client_name=project_data["client_name"],
                project_name=project_data["project_name"],
                source_lang=project_data["source_lang"],
                target_lang=project_data["target_lang"],
                content_type=project_data["content_type"],
                desired_deadline=project_data["desired_deadline"],
                organization_id=org.id,
                created_by=manager_user.id
            )
            db.session.add(project)
            created_projects.append(project)
        
        db.session.commit()
        print(f"✅ Created {len(created_projects)} projects")
        
        # Create sample documents
        print("📄 Creating sample documents...")
        documents_data = [
            {
                "filename": "legal_contract.pdf",
                "content": "CONTRATO DE SERVICIOS LINGÜÍSTICOS\n\nPARTIES:\n- Provider: Global Language Solutions Inc.\n- Client: International Tech Corporation\n\nSCOPE OF SERVICES:\n1. Translation Services\n2. Quality Assurance\n3. Project Management\n\nTECHNICAL REQUIREMENTS:\n- CAT tools: SDL Trados Studio, MemoQ\n- File formats: PDF, DOCX, XLSX\n- Quality standards: ISO 17100:2015\n\nPRICING STRUCTURE:\n- Standard translation: $0.15 per word\n- Rush translation: $0.25 per word\n- Technical review: $0.08 per word",
                "type": "legal_contract"
            },
            {
                "filename": "technical_spec.pdf",
                "content": "TECHNICAL SPECIFICATION MANUAL\nAI-Powered Translation Management System\n\nSYSTEM ARCHITECTURE:\n\n1. FRONTEND COMPONENTS\n- React.js SPA with TypeScript\n- Material-UI component library\n- Redux state management\n- WebSocket real-time updates\n\n2. BACKEND SERVICES\n- Python Flask REST API\n- PostgreSQL database with JSONB support\n- Redis caching layer\n- Celery task queue\n\n3. AI/ML INTEGRATION\n- OpenAI GPT-4 API integration\n- Custom fine-tuned models\n- Neural machine translation\n- Quality prediction algorithms\n\nPERFORMANCE METRICS:\n- API response time: < 200ms\n- Translation accuracy: > 95%\n- System uptime: 99.9%\n- Concurrent users: 1000+",
                "type": "technical_spec"
            },
            {
                "filename": "medical_research.pdf",
                "content": "CLINICAL RESEARCH STUDY\nComparative Analysis of Machine Translation Quality\nin Medical Documentation: A Multi-Center Study\n\nABSTRACT:\nThis study evaluates the effectiveness of AI-powered translation\nsystems in medical documentation across five European hospitals.\nWe analyzed 1,000 medical reports translated from English to\nSpanish, French, German, and Italian using both traditional\nhuman translation and AI-assisted methods.\n\nMETHODOLOGY:\n- Prospective, randomized, controlled trial\n- Multi-center study across 5 European hospitals\n- Double-blind evaluation by medical professionals\n- Statistical analysis using mixed-effects models\n\nRESULTS:\n- Human translation: 97.2% accuracy\n- AI-assisted translation: 94.8% accuracy\n- Hybrid approach: 96.1% accuracy\n\nCONCLUSIONS:\n1. AI translation shows promising results in medical documentation\n2. Human oversight remains essential for patient safety\n3. Hybrid approaches offer optimal balance of speed and accuracy",
                "type": "medical_research"
            }
        ]
        
        # Create document files
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        for doc_data in documents_data:
            # Create document file
            doc_path = uploads_dir / doc_data["filename"]
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(doc_data["content"])
            
            # Create document record
            doc = ProjectDocument(
                project_id=created_projects[0].id,  # Assign to first project
                file_name=doc_data["filename"],
                file_path=str(doc_path),
                file_type="pdf",
                word_count=len(doc_data["content"].split()),
                status="Uploaded"
            )
            db.session.add(doc)
        
        db.session.commit()
        print(f"✅ Created {len(documents_data)} sample documents")
        
        print("\n🎉 Sample data creation completed!")
        print("\n📊 Summary:")
        print(f"   - Organization: {org.name}")
        print(f"   - Users: 3 (admin, manager, client)")
        print(f"   - Linguists: {len(created_linguists)}")
        print(f"   - Projects: {len(created_projects)}")
        print(f"   - Documents: {len(documents_data)}")
        
        print("\n🔑 Login Credentials:")
        print("   - Admin: admin@gpo.com / admin123")
        print("   - Manager: manager@gpo.com / manager123")
        print("   - Client: client@gpo.com / client123")
        
        print("\n🌐 Access Your Application:")
        print("   - URL: http://localhost:5001")
        print("   - Dashboard: http://localhost:5001/dashboard")

if __name__ == "__main__":
    create_sample_data() 