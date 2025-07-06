#!/usr/bin/env python3
"""
Full GPO Application Test Scenario
This script creates a comprehensive test scenario with complex documents
that require AI analysis and processing.
"""

import os
import sys
import uuid
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from database import User, Organization, Project, ProjectDocument, Linguist
from auth import init_auth

def create_complex_documents():
    """Create complex documents that require AI analysis"""
    
    documents = [
        {
            "filename": "legal_contract_multilingual.pdf",
            "content": """
            CONTRATO DE SERVICIOS LINGÜÍSTICOS
            SERVICE AGREEMENT FOR LINGUISTIC SERVICES
            CONTRAT DE SERVICES LINGUISTIQUES
            
            PARTIES:
            - Provider: Global Language Solutions Inc.
            - Client: International Tech Corporation
            
            SCOPE OF SERVICES:
            1. Translation Services
               - Technical documentation (EN ↔ ES, FR, DE, IT, PT)
               - Legal documents and contracts
               - Marketing materials and website content
               - Software localization and UI/UX text
            
            2. Quality Assurance
               - Multi-stage review process
               - Terminology consistency checks
               - Cultural adaptation and localization
               - Final proofreading and validation
            
            3. Project Management
               - Dedicated project manager
               - Regular progress updates
               - Risk assessment and mitigation
               - Quality metrics reporting
            
            TECHNICAL REQUIREMENTS:
            - CAT tools: SDL Trados Studio, MemoQ, Wordfast
            - File formats: PDF, DOCX, XLSX, XML, JSON, HTML
            - Translation memory management
            - Terminology database maintenance
            
            QUALITY STANDARDS:
            - ISO 17100:2015 compliance
            - 99.5% accuracy requirement
            - 48-hour turnaround for urgent requests
            - Unlimited revision cycles within 30 days
            
            PRICING STRUCTURE:
            - Standard translation: $0.15 per word
            - Rush translation: $0.25 per word
            - Technical review: $0.08 per word
            - Project management: 15% of translation cost
            
            DELIVERABLES:
            - Translated files in original format
            - Translation memory files
            - Quality assurance report
            - Certificate of accuracy
            
            CONFIDENTIALITY:
            - NDA compliance required
            - Secure file transfer protocols
            - Data retention: 2 years
            - GDPR compliance for EU projects
            """,
            "type": "legal_contract",
            "languages": ["en", "es", "fr", "de", "it", "pt"],
            "complexity": "high"
        },
        {
            "filename": "technical_specification_manual.pdf",
            "content": """
            TECHNICAL SPECIFICATION MANUAL
            AI-Powered Translation Management System
            
            SYSTEM ARCHITECTURE:
            
            1. FRONTEND COMPONENTS
               - React.js SPA with TypeScript
               - Material-UI component library
               - Redux state management
               - WebSocket real-time updates
               - Progressive Web App capabilities
            
            2. BACKEND SERVICES
               - Python Flask REST API
               - PostgreSQL database with JSONB support
               - Redis caching layer
               - Celery task queue
               - Docker containerization
            
            3. AI/ML INTEGRATION
               - OpenAI GPT-4 API integration
               - Custom fine-tuned models
               - Neural machine translation
               - Quality prediction algorithms
               - Automated terminology extraction
            
            4. TRANSLATION WORKFLOW
               - Document preprocessing and analysis
               - AI-powered content categorization
               - Automatic language detection
               - Terminology extraction and management
               - Translation memory matching
               - Quality assurance automation
            
            TECHNICAL REQUIREMENTS:
            
            Performance Metrics:
            - API response time: < 200ms
            - Translation accuracy: > 95%
            - System uptime: 99.9%
            - Concurrent users: 1000+
            
            Security Standards:
            - OAuth 2.0 authentication
            - JWT token management
            - End-to-end encryption
            - SOC 2 Type II compliance
            - GDPR data protection
            
            Integration Points:
            - CAT tool APIs (SDL, MemoQ, Wordfast)
            - Cloud storage (AWS S3, Google Cloud)
            - Payment gateways (Stripe, PayPal)
            - Communication platforms (Slack, Teams)
            
            DATA PROCESSING PIPELINE:
            
            Phase 1: Document Analysis
            - File format detection and conversion
            - Content structure analysis
            - Language identification
            - Complexity assessment
            
            Phase 2: AI Processing
            - Content categorization
            - Terminology extraction
            - Translation memory matching
            - Quality prediction
            
            Phase 3: Human Review
            - Expert linguist assignment
            - Quality assurance review
            - Final validation
            - Client approval workflow
            
            QUALITY ASSURANCE FRAMEWORK:
            
            Automated Checks:
            - Grammar and spelling validation
            - Terminology consistency
            - Format preservation
            - Character count verification
            
            Human Review:
            - Expert linguist review
            - Technical accuracy check
            - Cultural adaptation
            - Final proofreading
            """,
            "type": "technical_spec",
            "languages": ["en"],
            "complexity": "very_high"
        },
        {
            "filename": "medical_research_paper.pdf",
            "content": """
            CLINICAL RESEARCH STUDY
            Comparative Analysis of Machine Translation Quality
            in Medical Documentation: A Multi-Center Study
            
            ABSTRACT:
            This study evaluates the effectiveness of AI-powered translation
            systems in medical documentation across five European hospitals.
            We analyzed 1,000 medical reports translated from English to
            Spanish, French, German, and Italian using both traditional
            human translation and AI-assisted methods.
            
            METHODOLOGY:
            
            Study Design:
            - Prospective, randomized, controlled trial
            - Multi-center study across 5 European hospitals
            - Double-blind evaluation by medical professionals
            - Statistical analysis using mixed-effects models
            
            Participants:
            - 50 medical professionals (10 per hospital)
            - 20 certified medical translators
            - 5 AI translation systems
            - 1,000 medical documents (200 per language pair)
            
            Document Types:
            - Patient medical records
            - Clinical trial protocols
            - Drug information leaflets
            - Medical device manuals
            - Research publications
            
            EVALUATION CRITERIA:
            
            Accuracy Metrics:
            - Medical terminology precision: 95% required
            - Clinical context preservation: 98% required
            - Patient safety compliance: 100% required
            - Regulatory compliance: 100% required
            
            Quality Dimensions:
            - Grammatical correctness
            - Medical terminology accuracy
            - Cultural adaptation
            - Readability and clarity
            - Consistency across documents
            
            RESULTS:
            
            Overall Performance:
            - Human translation: 97.2% accuracy
            - AI-assisted translation: 94.8% accuracy
            - Hybrid approach: 96.1% accuracy
            
            Language-Specific Results:
            - English to Spanish: 95.1% accuracy
            - English to French: 94.3% accuracy
            - English to German: 93.8% accuracy
            - English to Italian: 94.9% accuracy
            
            Document Type Performance:
            - Patient records: 96.2% accuracy
            - Clinical protocols: 94.1% accuracy
            - Drug information: 95.8% accuracy
            - Device manuals: 93.5% accuracy
            
            CONCLUSIONS:
            
            Key Findings:
            1. AI translation shows promising results in medical documentation
            2. Human oversight remains essential for patient safety
            3. Hybrid approaches offer optimal balance of speed and accuracy
            4. Language-specific training improves performance significantly
            
            Clinical Implications:
            - Reduced translation costs by 40%
            - Faster document turnaround (48 hours vs 5 days)
            - Improved consistency across translations
            - Enhanced accessibility for non-English speakers
            
            Future Directions:
            - Development of medical-specific AI models
            - Integration with electronic health records
            - Real-time translation for telemedicine
            - Automated quality assurance systems
            """,
            "type": "medical_research",
            "languages": ["en", "es", "fr", "de", "it"],
            "complexity": "very_high"
        },
        {
            "filename": "financial_quarterly_report.pdf",
            "content": """
            QUARTERLY FINANCIAL REPORT
            Global Language Services Market Analysis
            Q4 2024 - Q1 2025
            
            EXECUTIVE SUMMARY:
            
            Market Overview:
            The global language services market reached $65.2 billion in 2024,
            representing a 12.3% year-over-year growth. AI integration has
            transformed traditional translation workflows, creating new
            opportunities and challenges for industry participants.
            
            KEY PERFORMANCE INDICATORS:
            
            Revenue Metrics:
            - Total market revenue: $65.2B (+12.3% YoY)
            - AI-powered services: $8.7B (+45.2% YoY)
            - Traditional services: $56.5B (+8.1% YoY)
            - Average project value: $2,847 (+15.7% YoY)
            
            Growth Drivers:
            - E-commerce globalization: +23.4%
            - Healthcare documentation: +18.7%
            - Legal services: +14.2%
            - Technical documentation: +16.9%
            
            TECHNOLOGY ADOPTION:
            
            AI Integration Levels:
            - Full AI adoption: 23% of companies
            - Partial AI integration: 47% of companies
            - Traditional methods only: 30% of companies
            
            Technology Stack Analysis:
            - Neural machine translation: 78% adoption
            - Computer-assisted translation: 92% adoption
            - Quality assurance automation: 65% adoption
            - Project management platforms: 88% adoption
            
            REGIONAL ANALYSIS:
            
            North America:
            - Market size: $24.8B (38.1% of global)
            - Growth rate: 14.2% YoY
            - Key players: 45% market share
            - Technology adoption: 85%
            
            Europe:
            - Market size: $18.9B (29.0% of global)
            - Growth rate: 11.8% YoY
            - Regulatory compliance: GDPR, ISO standards
            - Quality focus: 92% accuracy requirement
            
            Asia-Pacific:
            - Market size: $12.7B (19.5% of global)
            - Growth rate: 18.4% YoY
            - Emerging markets: China, India, Southeast Asia
            - Mobile-first approach: 78% mobile usage
            
            COMPETITIVE LANDSCAPE:
            
            Market Leaders:
            1. Lionbridge Technologies: $1.2B revenue
            2. TransPerfect: $1.1B revenue
            3. SDL plc: $890M revenue
            4. RWS Holdings: $780M revenue
            5. Welocalize: $420M revenue
            
            Competitive Advantages:
            - Technology innovation: 35% of differentiation
            - Quality assurance: 28% of differentiation
            - Global presence: 22% of differentiation
            - Industry expertise: 15% of differentiation
            
            FUTURE OUTLOOK:
            
            Market Projections:
            - 2025 market size: $73.8B (+13.2%)
            - 2026 market size: $83.1B (+12.6%)
            - 2027 market size: $93.4B (+12.4%)
            
            Emerging Trends:
            - Real-time translation services
            - Voice and video translation
            - Augmented reality localization
            - Blockchain-based quality verification
            
            Investment Opportunities:
            - AI/ML technology development
            - Quality assurance automation
            - Emerging market expansion
            - Industry-specific solutions
            """,
            "type": "financial_report",
            "languages": ["en", "es", "fr", "de", "zh", "ja"],
            "complexity": "high"
        },
        {
            "filename": "software_user_manual.pdf",
            "content": """
            SOFTWARE USER MANUAL
            Advanced Translation Management System v3.2
            
            SYSTEM OVERVIEW:
            
            The Advanced Translation Management System (ATMS) is a
            comprehensive platform designed for professional translation
            agencies and corporate language departments. It integrates
            AI-powered translation capabilities with human expertise
            to deliver high-quality, cost-effective translation services.
            
            CORE FEATURES:
            
            1. PROJECT MANAGEMENT
               - Multi-project workflow management
               - Resource allocation and scheduling
               - Progress tracking and reporting
               - Client communication portal
               - Automated invoicing and billing
            
            2. TRANSLATION WORKFLOW
               - Document preprocessing and analysis
               - AI-powered translation suggestions
               - Human review and editing interface
               - Quality assurance automation
               - Final delivery and archiving
            
            3. QUALITY ASSURANCE
               - Automated grammar and spelling checks
               - Terminology consistency validation
               - Format preservation verification
               - Cultural adaptation guidelines
               - Client feedback integration
            
            4. RESOURCE MANAGEMENT
               - Linguist database and profiles
               - Translation memory management
               - Terminology database maintenance
               - Style guide enforcement
               - Performance analytics
            
            TECHNICAL SPECIFICATIONS:
            
            System Requirements:
            - Operating System: Windows 10+, macOS 10.15+, Linux
            - Processor: Intel i5 or AMD equivalent
            - Memory: 8GB RAM minimum, 16GB recommended
            - Storage: 50GB available space
            - Network: Broadband internet connection
            
            Supported File Formats:
            - Documents: DOCX, PDF, RTF, TXT, HTML
            - Spreadsheets: XLSX, CSV, TSV
            - Presentations: PPTX, PPT
            - Graphics: SVG, PNG, JPG
            - Code: XML, JSON, YAML, PO
            
            Integration Capabilities:
            - CAT tool integration (SDL, MemoQ, Wordfast)
            - Cloud storage (Google Drive, Dropbox, OneDrive)
            - Project management tools (Jira, Asana, Trello)
            - Communication platforms (Slack, Teams, Zoom)
            - Payment gateways (Stripe, PayPal, Square)
            
            USER INTERFACE:
            
            Dashboard:
            - Project overview and statistics
            - Recent activity feed
            - Quick action buttons
            - Notification center
            - Search functionality
            
            Project Workspace:
            - Document viewer and editor
            - Translation memory panel
            - Terminology database
            - Quality check results
            - Collaboration tools
            
            ADMINISTRATION:
            
            User Management:
            - Role-based access control
            - Permission management
            - Activity logging
            - Security settings
            - Backup and recovery
            
            System Configuration:
            - Workflow customization
            - Quality metrics setup
            - Integration settings
            - Notification preferences
            - Performance optimization
            
            TROUBLESHOOTING:
            
            Common Issues:
            1. Connection problems: Check network settings
            2. File upload errors: Verify file format and size
            3. Translation quality: Review AI model settings
            4. Performance issues: Clear cache and restart
            5. Integration errors: Check API credentials
            
            Support Resources:
            - Online documentation and tutorials
            - Video training materials
            - Community forum and discussions
            - Technical support ticketing
            - Live chat assistance
            """,
            "type": "software_manual",
            "languages": ["en", "es", "fr", "de", "it", "pt", "ru"],
            "complexity": "high"
        }
    ]
    
    return documents

def create_test_users():
    """Create test users with different roles"""
    
    users = [
        {
            "email": "admin@gpo.com",
            "name": "Admin User",
            "password": "admin123",
            "role": "admin"
        },
        {
            "email": "manager@gpo.com",
            "name": "Project Manager",
            "password": "manager123",
            "role": "manager"
        },
        {
            "email": "linguist1@gpo.com",
            "name": "Senior Linguist - Spanish",
            "password": "linguist123",
            "role": "linguist"
        },
        {
            "email": "linguist2@gpo.com",
            "name": "Technical Translator - French",
            "password": "linguist123",
            "role": "linguist"
        },
        {
            "email": "client1@gpo.com",
            "name": "Tech Corp Client",
            "password": "client123",
            "role": "client"
        }
    ]
    
    return users

def create_test_linguists():
    """Create test linguists with different specializations"""
    
    linguists = [
        {
            "name": "Dr. Maria Rodriguez",
            "email": "maria.rodriguez@linguists.com",
            "phone": "+34 91 123 4567",
            "languages": ["en", "es", "fr"],
            "specializations": ["medical", "legal", "technical"],
            "experience_years": 15,
            "hourly_rate": 45.00,
            "availability": "full_time",
            "certifications": ["ATA", "ISO 17100", "Medical Translation"]
        },
        {
            "name": "Jean-Pierre Dubois",
            "email": "jean.dubois@linguists.com",
            "phone": "+33 1 42 34 5678",
            "languages": ["en", "fr", "de"],
            "specializations": ["financial", "technical", "software"],
            "experience_years": 12,
            "hourly_rate": 42.00,
            "availability": "full_time",
            "certifications": ["DGT", "Technical Translation", "Software Localization"]
        },
        {
            "name": "Hans Mueller",
            "email": "hans.mueller@linguists.com",
            "phone": "+49 30 1234 5678",
            "languages": ["en", "de", "it"],
            "specializations": ["engineering", "automotive", "technical"],
            "experience_years": 18,
            "hourly_rate": 48.00,
            "availability": "full_time",
            "certifications": ["BDÜ", "Engineering Translation", "ISO 9001"]
        },
        {
            "name": "Sofia Bianchi",
            "email": "sofia.bianchi@linguists.com",
            "phone": "+39 02 1234 5678",
            "languages": ["en", "it", "es"],
            "specializations": ["marketing", "creative", "literary"],
            "experience_years": 10,
            "hourly_rate": 38.00,
            "availability": "part_time",
            "certifications": ["AITI", "Creative Translation", "Marketing Localization"]
        },
        {
            "name": "Carlos Santos",
            "email": "carlos.santos@linguists.com",
            "phone": "+55 11 98765 4321",
            "languages": ["en", "pt", "es"],
            "specializations": ["medical", "pharmaceutical", "regulatory"],
            "experience_years": 14,
            "hourly_rate": 44.00,
            "availability": "full_time",
            "certifications": ["ABRATES", "Medical Translation", "FDA Compliance"]
        }
    ]
    
    return linguists

def create_test_projects():
    """Create test projects with different complexities"""
    
    projects = [
        {
            "title": "Medical Device Documentation Translation",
            "description": "Comprehensive translation of medical device user manuals, safety instructions, and regulatory documentation for EU market entry.",
            "client_name": "MedTech Solutions Inc.",
            "source_language": "en",
            "target_languages": ["es", "fr", "de", "it"],
            "project_type": "medical",
            "complexity": "high",
            "deadline": datetime.now() + timedelta(days=30),
            "budget": 25000.00,
            "status": "in_progress"
        },
        {
            "title": "Software Localization for E-commerce Platform",
            "description": "Full localization of e-commerce platform including UI/UX text, product descriptions, and customer support documentation.",
            "client_name": "Global Retail Corp",
            "source_language": "en",
            "target_languages": ["es", "fr", "de", "it", "pt", "ru"],
            "project_type": "software",
            "complexity": "very_high",
            "deadline": datetime.now() + timedelta(days=45),
            "budget": 45000.00,
            "status": "planning"
        },
        {
            "title": "Legal Contract Translation and Review",
            "description": "Translation and legal review of international service agreements, ensuring compliance with local regulations.",
            "client_name": "International Law Firm",
            "source_language": "en",
            "target_languages": ["es", "fr", "de"],
            "project_type": "legal",
            "complexity": "high",
            "deadline": datetime.now() + timedelta(days=21),
            "budget": 18000.00,
            "status": "in_progress"
        },
        {
            "title": "Financial Report Translation",
            "description": "Translation of quarterly financial reports and investor communications for multinational corporation.",
            "client_name": "Global Finance Group",
            "source_language": "en",
            "target_languages": ["es", "fr", "de", "zh", "ja"],
            "project_type": "financial",
            "complexity": "medium",
            "deadline": datetime.now() + timedelta(days=14),
            "budget": 12000.00,
            "status": "completed"
        },
        {
            "title": "Technical Manual Translation",
            "description": "Translation of complex technical documentation for industrial machinery, including safety protocols and maintenance procedures.",
            "client_name": "Industrial Equipment Ltd",
            "source_language": "en",
            "target_languages": ["es", "fr", "de", "it"],
            "project_type": "technical",
            "complexity": "very_high",
            "deadline": datetime.now() + timedelta(days=60),
            "budget": 35000.00,
            "status": "planning"
        }
    ]
    
    return projects

def run_full_test_scenario():
    """Run the complete test scenario"""
    
    print("🚀 Starting Full GPO Test Scenario")
    print("=" * 50)
    
    with app.app_context():
        # Initialize database
        db.create_all()
        
        # Create test organization
        print("📋 Creating test organization...")
        org = Organization(
            id=str(uuid.uuid4()),
            name="GPO Test Organization",
            subscription_tier="premium",
            max_users=50,
            max_projects=100
        )
        db.session.add(org)
        db.session.commit()
        
        # Create test users
        print("👥 Creating test users...")
        users_data = create_test_users()
        created_users = {}
        
        for user_data in users_data:
            user = User(
                id=str(uuid.uuid4()),
                email=user_data["email"],
                name=user_data["name"],
                role=user_data["role"],
                organization_id=org.id
            )
            user.set_password(user_data["password"])
            db.session.add(user)
            created_users[user_data["email"]] = user
        
        db.session.commit()
        
        # Create test linguists
        print("🎓 Creating test linguists...")
        linguists_data = create_test_linguists()
        created_linguists = {}
        
        for linguist_data in linguists_data:
            linguist = Linguist(
                id=str(uuid.uuid4()),
                name=linguist_data["name"],
                email=linguist_data["email"],
                phone=linguist_data["phone"],
                languages=",".join(linguist_data["languages"]),
                specializations=",".join(linguist_data["specializations"]),
                experience_years=linguist_data["experience_years"],
                hourly_rate=linguist_data["hourly_rate"],
                availability=linguist_data["availability"],
                certifications=",".join(linguist_data["certifications"]),
                organization_id=org.id
            )
            db.session.add(linguist)
            created_linguists[linguist_data["email"]] = linguist
        
        db.session.commit()
        
        # Create test projects
        print("📁 Creating test projects...")
        projects_data = create_test_projects()
        created_projects = {}
        
        for project_data in projects_data:
            project = Project(
                id=str(uuid.uuid4()),
                title=project_data["title"],
                description=project_data["description"],
                client_name=project_data["client_name"],
                source_language=project_data["source_language"],
                target_languages=",".join(project_data["target_languages"]),
                project_type=project_data["project_type"],
                complexity=project_data["complexity"],
                deadline=project_data["deadline"],
                budget=project_data["budget"],
                status=project_data["status"],
                organization_id=org.id,
                created_by=created_users["manager@gpo.com"].id
            )
            db.session.add(project)
            created_projects[project_data["title"]] = project
        
        db.session.commit()
        
        # Create complex documents
        print("📄 Creating complex test documents...")
        documents_data = create_complex_documents()
        
        for doc_data in documents_data:
            # Create document file
            doc_path = Path("uploads") / doc_data["filename"]
            doc_path.parent.mkdir(exist_ok=True)
            
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(doc_data["content"])
            
            # Create document record
            doc = ProjectDocument(
                id=str(uuid.uuid4()),
                filename=doc_data["filename"],
                original_filename=doc_data["filename"],
                file_path=str(doc_path),
                file_size=len(doc_data["content"]),
                document_type=doc_data["type"],
                source_language="en",
                target_languages=",".join(doc_data["languages"]),
                complexity=doc_data["complexity"],
                status="uploaded",
                organization_id=org.id,
                uploaded_by=created_users["client1@gpo.com"].id
            )
            db.session.add(doc)
        
        db.session.commit()
        
        print("✅ Test scenario completed successfully!")
        print("\n📊 Test Data Summary:")
        print(f"   - Organizations: 1")
        print(f"   - Users: {len(created_users)}")
        print(f"   - Linguists: {len(created_linguists)}")
        print(f"   - Projects: {len(created_projects)}")
        print(f"   - Documents: {len(documents_data)}")
        
        print("\n🔑 Test Login Credentials:")
        for email, password in [("admin@gpo.com", "admin123"), 
                               ("manager@gpo.com", "manager123"),
                               ("client1@gpo.com", "client123")]:
            print(f"   - {email} / {password}")
        
        print("\n🎯 Next Steps:")
        print("   1. Start the application: python app.py")
        print("   2. Login with test credentials")
        print("   3. Navigate to /dashboard to see projects")
        print("   4. Check /linguists for available linguists")
        print("   5. Upload documents and assign to projects")
        print("   6. Test AI analysis workflow")

if __name__ == "__main__":
    run_full_test_scenario() 