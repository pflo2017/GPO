from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from faker import Faker
import random

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Supabase PostgreSQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:UCOXZibz5OLgTofg@db.dbbpghthgnwozewmlzes.supabase.co:6543/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
fake = Faker()

# Database Models
class Linguist(db.Model):
    __tablename__ = 'linguists'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    languages = db.Column(db.Text, nullable=False)
    specialties = db.Column(db.Text, nullable=False)
    speed_score = db.Column(db.Integer, nullable=False)
    quality_score = db.Column(db.Integer, nullable=False)
    current_load = db.Column(db.Text, nullable=False)

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    client_name = db.Column(db.Text, nullable=False)
    project_name = db.Column(db.Text, nullable=False)
    language_pair = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    initial_word_count = db.Column(db.Integer, nullable=False)
    translated_words = db.Column(db.Integer, nullable=False)
    assigned_linguist_id = db.Column(db.BigInteger)
    status = db.Column(db.Text, nullable=False)
    gpo_risk_status = db.Column(db.Text)
    gpo_risk_reason = db.Column(db.Text)
    gpo_recommendation = db.Column(db.Text)
    source_file_path = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-dummy-data')
def generate_dummy_data():
    """Generate realistic dummy data for testing GPO system"""
    try:
        # Generate linguists
        linguists_data = generate_linguists()
        for linguist_data in linguists_data:
            linguist = Linguist(**linguist_data)
            db.session.add(linguist)
        
        db.session.commit()
        
        # Get linguist IDs for project assignment
        linguist_ids = [l.id for l in Linguist.query.all()]
        
        # Generate projects
        projects_data = generate_projects(linguist_ids)
        for project_data in projects_data:
            project = Project(**project_data)
            db.session.add(project)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(linguists_data)} linguists and {len(projects_data)} projects',
            'linguists_count': len(linguists_data),
            'projects_count': len(projects_data)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/dashboard')
def dashboard():
    """Main dashboard showing projects and GPO insights"""
    projects = Project.query.all()
    linguists = Linguist.query.all()

    # Convert SQLAlchemy objects to dicts for JSON serialization
    def project_to_dict(p):
        return {
            'id': p.id,
            'client_name': p.client_name,
            'project_name': p.project_name,
            'language_pair': p.language_pair,
            'content_type': p.content_type,
            'start_date': str(p.start_date),
            'due_date': str(p.due_date),
            'initial_word_count': p.initial_word_count,
            'translated_words': p.translated_words,
            'assigned_linguist_id': p.assigned_linguist_id,
            'status': p.status,
            'gpo_risk_status': p.gpo_risk_status,
            'gpo_risk_reason': p.gpo_risk_reason,
            'gpo_recommendation': p.gpo_recommendation,
            'source_file_path': p.source_file_path,
            'created_at': str(p.created_at)
        }
    def linguist_to_dict(l):
        return {
            'id': l.id,
            'name': l.name,
            'languages': l.languages,
            'specialties': l.specialties,
            'speed_score': l.speed_score,
            'quality_score': l.quality_score,
            'current_load': l.current_load
        }

    projects_dict = [project_to_dict(p) for p in projects]
    linguists_dict = [linguist_to_dict(l) for l in linguists]

    # Calculate GPO metrics
    total_projects = len(projects)
    high_risk_projects = len([p for p in projects if p.gpo_risk_status == 'High'])
    medium_risk_projects = len([p for p in projects if p.gpo_risk_status == 'Medium'])
    low_risk_projects = len([p for p in projects if p.gpo_risk_status == 'Low'])

    return render_template('dashboard.html', 
                         projects=projects_dict, 
                         linguists=linguists_dict,
                         total_projects=total_projects,
                         high_risk=high_risk_projects,
                         medium_risk=medium_risk_projects,
                         low_risk=low_risk_projects)

def generate_linguists():
    """Generate realistic linguist data"""
    languages_list = [
        "English-Spanish", "English-French", "English-German", "English-Italian",
        "English-Portuguese", "English-Russian", "English-Chinese", "English-Japanese",
        "English-Korean", "English-Arabic", "Spanish-French", "German-French"
    ]
    
    specialties_list = [
        "Medical", "Legal", "Technical", "Marketing", "Financial", "Academic",
        "Pharmaceutical", "IT/Software", "Manufacturing", "Tourism", "Education"
    ]
    
    linguists = []
    for i in range(15):  # Generate 15 linguists
        linguist = {
            'name': fake.name(),
            'languages': random.choice(languages_list),
            'specialties': random.choice(specialties_list),
            'speed_score': random.randint(60, 95),
            'quality_score': random.randint(70, 98),
            'current_load': random.choice(['Low', 'Medium', 'High', 'Overloaded'])
        }
        linguists.append(linguist)
    
    return linguists

def generate_projects(linguist_ids):
    """Generate realistic project data with GPO risk assessment"""
    content_types = [
        "Medical Documentation", "Legal Contracts", "Technical Manuals", 
        "Marketing Materials", "Financial Reports", "Academic Papers",
        "Pharmaceutical Labels", "Software Documentation", "User Manuals",
        "Training Materials", "Website Content", "Press Releases"
    ]
    
    statuses = ["In Progress", "Pending Review", "Completed", "On Hold", "Cancelled"]
    clients = ["MedCorp Inc.", "LegalTech Solutions", "Global Manufacturing", 
               "Financial Services Ltd.", "Academic Publishing Co.", "PharmaTech",
               "Software Solutions Inc.", "Tourism Board", "Education First"]
    
    projects = []
    for i in range(25):  # Generate 25 projects
        start_date = fake.date_between(start_date='-30d', end_date='+10d')
        due_date = fake.date_between(start_date=start_date, end_date='+60d')
        
        initial_words = random.randint(1000, 50000)
        translated_words = random.randint(0, initial_words)
        
        # GPO Risk Assessment Logic
        risk_status, risk_reason, recommendation = assess_gpo_risks(
            start_date, due_date, initial_words, translated_words, content_types[i % len(content_types)]
        )
        
        project = {
            'client_name': random.choice(clients),
            'project_name': f"{fake.word().title()} {fake.word().title()} Translation",
            'language_pair': random.choice(["English-Spanish", "English-French", "English-German", "English-Chinese"]),
            'content_type': content_types[i % len(content_types)],
            'start_date': start_date,
            'due_date': due_date,
            'initial_word_count': initial_words,
            'translated_words': translated_words,
            'assigned_linguist_id': random.choice(linguist_ids) if linguist_ids else None,
            'status': random.choice(statuses),
            'gpo_risk_status': risk_status,
            'gpo_risk_reason': risk_reason,
            'gpo_recommendation': recommendation,
            'source_file_path': f"dummy_docs/project_{i+1}_source.docx"
        }
        projects.append(project)
    
    return projects

def assess_gpo_risks(start_date, due_date, initial_words, translated_words, content_type):
    """GPO AI logic to assess project risks and provide recommendations"""
    days_remaining = (due_date - datetime.now().date()).days
    progress_percentage = (translated_words / initial_words) * 100 if initial_words > 0 else 0
    daily_words_needed = (initial_words - translated_words) / max(days_remaining, 1)
    
    risk_factors = []
    recommendations = []
    
    # Deadline Risk
    if days_remaining < 7:
        risk_factors.append("Critical deadline approaching")
        recommendations.append("Expedite review process")
    elif days_remaining < 14:
        risk_factors.append("Tight deadline")
        recommendations.append("Consider additional resources")
    
    # Progress Risk
    if progress_percentage < 30 and days_remaining < 21:
        risk_factors.append("Behind schedule")
        recommendations.append("Reassign to faster linguist")
    
    # Content Type Risk
    if content_type in ["Medical Documentation", "Legal Contracts", "Pharmaceutical Labels"]:
        risk_factors.append("Sensitive content requiring specialized review")
        recommendations.append("Assign medical/legal specialist")
    
    # Word Count Risk
    if daily_words_needed > 2000:
        risk_factors.append("High daily word count requirement")
        recommendations.append("Split project or add resources")
    
    # Determine overall risk status
    if len(risk_factors) >= 3:
        risk_status = "High"
    elif len(risk_factors) >= 2:
        risk_status = "Medium"
    elif len(risk_factors) >= 1:
        risk_status = "Low"
    else:
        risk_status = "None"
    
    risk_reason = "; ".join(risk_factors) if risk_factors else "No significant risks identified"
    recommendation = "; ".join(recommendations) if recommendations else "Continue current approach"
    
    return risk_status, risk_reason, recommendation

if __name__ == '__main__':
    app.run(debug=True, port=5005) 