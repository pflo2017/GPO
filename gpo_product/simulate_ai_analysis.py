#!/usr/bin/env python
"""
GPO AI Analysis Simulator

This script simulates AI analysis for different document types, generating realistic
analysis results that would typically come from a sophisticated AI model.

Usage:
    python simulate_ai_analysis.py <project_id>
"""

import sys
import os
import json
import uuid
import random
from datetime import datetime, timedelta
import argparse
from sqlalchemy import create_engine, text
import re

# Document type-specific analysis templates
ANALYSIS_TEMPLATES = {
    "legal": {
        "risk_levels": ["High", "Medium-High", "Medium"],
        "risk_factors": [
            "Contains potential PII data",
            "Complex legal terminology requiring specialist knowledge",
            "Contains jurisdiction-specific clauses",
            "Includes regulatory compliance requirements",
            "Contains confidentiality clauses",
            "Includes intellectual property provisions"
        ],
        "challenges": [
            "Complex legal terminology requiring specialist knowledge",
            "Jurisdiction-specific legal concepts that may not have direct equivalents",
            "Formal register with precise terminology requirements",
            "References to specific laws and regulations that may differ across jurisdictions",
            "Extensive use of legal boilerplate that requires consistent translation",
            "Contains legal citations and references requiring research"
        ],
        "sensitive_data": [
            "Potential PII detected in sections {section_numbers}",
            "Confidential business information in clauses {section_numbers}",
            "Financial data identified in sections {section_numbers}",
            "Personally identifiable information requiring special handling in section {section_numbers}",
            "Contractual terms with confidentiality requirements in sections {section_numbers}"
        ],
        "recommendations": [
            "Assign a legal specialist translator with at least {years} years of experience",
            "Implement pre-translation legal terminology review",
            "Conduct jurisdiction-specific legal review before delivery",
            "Use specialized legal translation memory",
            "Schedule additional time for legal terminology research",
            "Allocate {percent}% more time due to legal complexity",
            "Implement dual review process with legal specialist"
        ],
        "linguist_requirements": [
            "Legal specialization with minimum {years} years experience",
            "Background in {specific_legal_field} law",
            "Experience with {jurisdiction} legal documents",
            "Certified legal translator with terminology expertise",
            "Previous experience with similar contract types",
            "Knowledge of both source and target legal systems"
        ]
    },
    "medical": {
        "risk_levels": ["High", "Medium-High", "Medium"],
        "risk_factors": [
            "Contains patient health information",
            "Complex medical terminology",
            "Regulatory compliance requirements",
            "Critical diagnostic information",
            "Treatment protocols requiring precision",
            "Pharmaceutical information requiring accuracy"
        ],
        "challenges": [
            "Specialized medical terminology requiring subject matter expertise",
            "Abbreviations and acronyms specific to medical field",
            "Critical information where translation errors could impact patient care",
            "References to specific medications and dosages requiring verification",
            "Anatomical terms requiring precise translation",
            "Medical procedures with region-specific protocols"
        ],
        "sensitive_data": [
            "Patient health information detected in sections {section_numbers}",
            "Diagnostic data requiring confidentiality in sections {section_numbers}",
            "Treatment protocols with sensitive information in sections {section_numbers}",
            "Medication information requiring verification in sections {section_numbers}",
            "Clinical trial data in sections {section_numbers}"
        ],
        "recommendations": [
            "Assign a medical specialist translator with minimum {years} years experience",
            "Implement terminology verification against medical databases",
            "Schedule additional review by subject matter expert",
            "Use specialized medical translation memory",
            "Allocate {percent}% more time for research and verification",
            "Implement dual translator review process"
        ],
        "linguist_requirements": [
            "Medical specialization with minimum {years} years experience",
            "Background in {specific_medical_field}",
            "Experience with similar document types",
            "Certified medical translator",
            "Knowledge of medical terminology in both source and target languages",
            "Previous experience with regulatory medical content"
        ]
    },
    "technical": {
        "risk_levels": ["Medium", "Medium-Low", "Low"],
        "risk_factors": [
            "Contains specialized technical terminology",
            "Includes technical specifications requiring precision",
            "Contains product safety information",
            "Includes technical diagrams with annotations",
            "Software interface elements requiring consistency",
            "Technical procedures requiring clear translation"
        ],
        "challenges": [
            "Specialized technical vocabulary requiring subject matter expertise",
            "Product-specific terminology requiring consistency",
            "Technical specifications with precise measurements and values",
            "Technical processes requiring clear sequential translation",
            "Interface elements requiring consistency with software",
            "Technical abbreviations and codes"
        ],
        "sensitive_data": [
            "Proprietary technical specifications in sections {section_numbers}",
            "Product design information in sections {section_numbers}",
            "Internal technical processes in sections {section_numbers}",
            "System architecture details in sections {section_numbers}",
            "Technical parameters requiring verification in sections {section_numbers}"
        ],
        "recommendations": [
            "Assign a technical specialist with background in {specific_tech_field}",
            "Create project-specific terminology database",
            "Schedule technical review with subject matter expert",
            "Use specialized technical translation memory",
            "Allocate {percent}% more time for technical research",
            "Implement consistency checks for technical terminology"
        ],
        "linguist_requirements": [
            "Technical specialization with minimum {years} years experience",
            "Background in {specific_tech_field}",
            "Experience with technical documentation",
            "Knowledge of technical standards in target market",
            "Previous experience with similar technical content",
            "Familiarity with technical diagrams and specifications"
        ]
    }
}

# Default fallback template for unknown document types
DEFAULT_TEMPLATE = {
    "risk_levels": ["Medium", "Low"],
    "risk_factors": [
        "General content complexity",
        "Specialized terminology",
        "Formatting requirements"
    ],
    "challenges": [
        "Domain-specific terminology",
        "Maintaining consistent tone and style",
        "Preserving formatting and layout"
    ],
    "sensitive_data": [
        "Potential business information in sections {section_numbers}",
        "Content requiring verification in sections {section_numbers}"
    ],
    "recommendations": [
        "Assign a translator with relevant subject expertise",
        "Create project-specific terminology list",
        "Allocate standard timeline for processing"
    ],
    "linguist_requirements": [
        "Experience with similar content types",
        "Knowledge of subject matter terminology",
        "Strong general translation skills"
    ]
}

def get_db_connection():
    """Create a database connection using environment variables or default values."""
    host = os.environ.get('SUPABASE_HOST', 'db.dbbpghthgnwozewmlzes.supabase.co')
    port = os.environ.get('SUPABASE_PORT', '5432')
    user = os.environ.get('SUPABASE_USER', 'postgres')
    password = os.environ.get('SUPABASE_PASSWORD', 'UCOXZibz5OLgTofg')
    db = os.environ.get('SUPABASE_DB', 'postgres')
    
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return create_engine(connection_string)

def get_project_details(conn, project_id):
    """Retrieve project details from the database."""
    result = conn.execute(text("""
        SELECT p.*, o.name as organization_name
        FROM projects p
        JOIN organizations o ON p.organization_id = o.id
        WHERE p.id = :project_id
    """), {"project_id": project_id})
    
    project = result.fetchone()
    if not project:
        return None
    
    # Get project documents
    docs_result = conn.execute(text("""
        SELECT * FROM project_documents 
        WHERE project_id = :project_id
    """), {"project_id": project_id})
    
    documents = docs_result.fetchall()
    
    return {
        "project": project,
        "documents": documents
    }

def extract_document_content(file_path):
    """Extract text content from a document file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error reading document: {e}")
        return ""

def analyze_content_type(content):
    """Determine the likely content type based on text analysis."""
    # Simple keyword-based classification
    legal_keywords = ['contract', 'agreement', 'party', 'clause', 'legal', 'terms', 'conditions', 'law', 'jurisdiction']
    medical_keywords = ['patient', 'treatment', 'diagnosis', 'medical', 'clinical', 'health', 'doctor', 'hospital', 'symptom']
    technical_keywords = ['system', 'technical', 'software', 'hardware', 'configuration', 'specification', 'interface', 'module']
    
    content_lower = content.lower()
    
    legal_score = sum(1 for keyword in legal_keywords if keyword in content_lower)
    medical_score = sum(1 for keyword in medical_keywords if keyword in content_lower)
    technical_score = sum(1 for keyword in technical_keywords if keyword in content_lower)
    
    scores = {
        'legal': legal_score,
        'medical': medical_score,
        'technical': technical_score
    }
    
    # Return the content type with the highest score, or default if all scores are low
    max_score = max(scores.values())
    if max_score > 2:  # Threshold for confidence
        return max(scores, key=scores.get)
    return "general"

def generate_section_numbers(max_sections=10):
    """Generate random section numbers for references."""
    num_sections = random.randint(1, 3)
    sections = sorted(random.sample(range(1, max_sections + 1), num_sections))
    
    if len(sections) == 1:
        return str(sections[0])
    elif len(sections) == 2:
        return f"{sections[0]} and {sections[1]}"
    else:
        return ", ".join(str(s) for s in sections[:-1]) + f", and {sections[-1]}"

def generate_analysis(content, content_type=None):
    """Generate AI analysis based on document content and type."""
    if not content_type:
        content_type = analyze_content_type(content)
    
    # Get the appropriate template
    template = ANALYSIS_TEMPLATES.get(content_type, DEFAULT_TEMPLATE)
    
    # Generate analysis components
    risk_level = random.choice(template["risk_levels"])
    risk_factors = random.sample(template["risk_factors"], k=min(3, len(template["risk_factors"])))
    challenges = random.sample(template["challenges"], k=min(3, len(template["challenges"])))
    
    # Format sensitive data alerts with random section numbers
    sensitive_data_templates = random.sample(template["sensitive_data"], k=min(2, len(template["sensitive_data"])))
    sensitive_data = [item.format(section_numbers=generate_section_numbers()) for item in sensitive_data_templates]
    
    # Format recommendations with random years and percentages
    recommendation_templates = random.sample(template["recommendations"], k=min(3, len(template["recommendations"])))
    recommendations = []
    for rec in recommendation_templates:
        if "{years}" in rec:
            rec = rec.format(years=random.randint(3, 8))
        if "{percent}" in rec:
            rec = rec.format(percent=random.choice([15, 20, 25, 30]))
        if "{specific_legal_field}" in rec:
            rec = rec.format(specific_legal_field=random.choice(["corporate", "intellectual property", "regulatory", "international"]))
        if "{specific_medical_field}" in rec:
            rec = rec.format(specific_medical_field=random.choice(["cardiology", "oncology", "neurology", "pharmaceuticals"]))
        if "{specific_tech_field}" in rec:
            rec = rec.format(specific_tech_field=random.choice(["software", "mechanical engineering", "electronics", "telecommunications"]))
        if "{jurisdiction}" in rec:
            rec = rec.format(jurisdiction=random.choice(["EU", "US", "international", "regional"]))
        recommendations.append(rec)
    
    # Format linguist requirements
    linguist_req_templates = random.sample(template["linguist_requirements"], k=min(3, len(template["linguist_requirements"])))
    linguist_requirements = []
    for req in linguist_req_templates:
        if "{years}" in req:
            req = req.format(years=random.randint(3, 8))
        if "{specific_legal_field}" in req:
            req = req.format(specific_legal_field=random.choice(["corporate", "intellectual property", "regulatory", "international"]))
        if "{specific_medical_field}" in req:
            req = req.format(specific_medical_field=random.choice(["cardiology", "oncology", "neurology", "pharmaceuticals"]))
        if "{specific_tech_field}" in req:
            req = req.format(specific_tech_field=random.choice(["software", "mechanical engineering", "electronics", "telecommunications"]))
        linguist_requirements.append(req)
    
    # Calculate word count and estimate completion time
    word_count = len(re.findall(r'\w+', content))
    base_words_per_day = 2500
    complexity_factor = 1.0
    if risk_level == "High":
        complexity_factor = 0.7
    elif risk_level == "Medium-High":
        complexity_factor = 0.8
    elif risk_level == "Medium":
        complexity_factor = 0.9
    
    estimated_days = round(word_count / (base_words_per_day * complexity_factor))
    if estimated_days < 1:
        estimated_days = 1
    
    # Generate the analysis object
    analysis = {
        "ai_analysis_id": str(uuid.uuid4()),
        "content_type": content_type,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "key_challenges": challenges,
        "sensitive_data_alerts": sensitive_data,
        "strategic_recommendations": recommendations,
        "linguist_requirements": linguist_requirements,
        "word_count": word_count,
        "estimated_completion_days": estimated_days,
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    return analysis

def update_project_with_analysis(conn, project_id, analysis):
    """Update the project in the database with the AI analysis results."""
    try:
        # Convert analysis to JSON string
        analysis_json = json.dumps(analysis)
        
        # Update the project record
        conn.execute(text("""
            UPDATE projects 
            SET 
                ai_analysis = :analysis,
                status = 'Analysis Complete',
                updated_at = NOW()
            WHERE id = :project_id
        """), {
            "analysis": analysis_json,
            "project_id": project_id
        })
        
        # Update documents status
        conn.execute(text("""
            UPDATE project_documents
            SET 
                status = 'Analyzed',
                updated_at = NOW()
            WHERE project_id = :project_id
        """), {
            "project_id": project_id
        })
        
        return True
    except Exception as e:
        print(f"Error updating project with analysis: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Simulate AI analysis for a GPO project')
    parser.add_argument('project_id', help='The UUID of the project to analyze')
    args = parser.parse_args()
    
    # Connect to the database
    engine = get_db_connection()
    with engine.connect() as conn:
        # Get project details
        project_data = get_project_details(conn, args.project_id)
        
        if not project_data:
            print(f"Project with ID {args.project_id} not found")
            return
        
        print(f"Analyzing project: {project_data['project'].name}")
        
        # Process each document
        all_content = ""
        for doc in project_data['documents']:
            print(f"Processing document: {doc.file_name}")
            content = extract_document_content(doc.file_path)
            all_content += content + "\n\n"
        
        if not all_content:
            print("No document content found to analyze")
            return
        
        # Generate AI analysis
        content_type = project_data['project'].content_type.lower() if project_data['project'].content_type else None
        analysis = generate_analysis(all_content, content_type)
        
        # Update the project with the analysis
        success = update_project_with_analysis(conn, args.project_id, analysis)
        
        if success:
            print(f"✅ Analysis complete for project {args.project_id}")
            print(f"Risk Level: {analysis['risk_level']}")
            print(f"Content Type: {analysis['content_type']}")
            print(f"Word Count: {analysis['word_count']}")
            print(f"Estimated Completion: {analysis['estimated_completion_days']} days")
        else:
            print("❌ Failed to update project with analysis")

if __name__ == "__main__":
    main() 