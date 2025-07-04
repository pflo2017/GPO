#!/usr/bin/env python3
"""
Database initialization script for GPO
"""

from datetime import datetime, timedelta
import random
import sys
import uuid
from faker import Faker
import os

# Create a Faker instance
fake = Faker()

# Import Flask and SQLAlchemy
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a minimal Flask app
app = Flask(__name__)

# Use SQLite for development
sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../gpo.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_path}"
print(f"⚠️ Using SQLite database at {sqlite_path}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from gpo_product.database import db

# Define the models (same as in app.py)
class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.Text, nullable=False)
    subscription_tier = db.Column(db.Text, default='free')
    subscription_status = db.Column(db.Text, default='active')
    subscription_start_date = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_end_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=365))
    max_users = db.Column(db.Integer, default=5)
    max_projects = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    organization = db.relationship('Organization', backref=db.backref('users', lazy=True))

class Linguist(db.Model):
    __tablename__ = 'linguists'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'))
    name = db.Column(db.Text, nullable=False)
    languages = db.Column(db.Text, nullable=False)
    specialties = db.Column(db.Text, nullable=False)
    speed_score = db.Column(db.Integer, nullable=False)
    quality_score = db.Column(db.Integer, nullable=False)
    current_load = db.Column(db.Text, nullable=False)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('linguist_profile', uselist=False))
    organization = db.relationship('Organization', backref=db.backref('linguists', lazy=True))

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
    assigned_linguist_id = db.Column(db.BigInteger, db.ForeignKey('linguists.id'))
    status = db.Column(db.Text, nullable=False)
    gpo_risk_status = db.Column(db.Text)
    gpo_risk_reason = db.Column(db.Text)
    gpo_recommendation = db.Column(db.Text)
    source_file_path = db.Column(db.Text)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    assigned_linguist = db.relationship('Linguist', backref=db.backref('projects', lazy=True))
    organization = db.relationship('Organization', backref=db.backref('projects', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_projects', lazy=True))

def init_db():
    """Initialize the database with sample data"""
    print('Creating database tables...')
    with app.app_context():
        db.create_all()
        
        print('Adding sample data...')
        # Create a sample organization
        org_id = str(uuid.uuid4())
        
        organization = Organization()
        organization.id = org_id
        organization.name = 'Sample Organization'
        organization.subscription_tier = 'professional'
        organization.subscription_status = 'active'
        organization.subscription_start_date = datetime.utcnow()
        organization.subscription_end_date = datetime.utcnow() + timedelta(days=365)
        organization.max_users = 25
        organization.max_projects = 200
        
        db.session.add(organization)
        db.session.commit()
        
        # Create a sample admin user
        admin_id = str(uuid.uuid4())
        
        admin = User()
        admin.id = admin_id
        admin.email = 'admin@example.com'
        admin.name = 'Admin User'
        admin.password_hash = 'pbkdf2:sha256:260000$rMQo1zAw$287773fcba3edc5db451c84c043abc0b7c7e5773f5f7f5e0a9c569b93e5bce4f'  # password: admin123
        admin.role = 'admin'
        admin.organization_id = org_id
        
        db.session.add(admin)
        db.session.commit()
        
        # Create sample linguists
        linguists = []
        for i in range(5):
            user_id = str(uuid.uuid4())
            
            # Create user first
            user = User()
            user.id = user_id
            user.email = f'linguist{i+1}@example.com'
            user.name = fake.name()
            user.password_hash = 'pbkdf2:sha256:260000$rMQo1zAw$287773fcba3edc5db451c84c043abc0b7c7e5773f5f7f5e0a9c569b93e5bce4f'  # password: admin123
            user.role = 'linguist'
            user.organization_id = org_id
            
            db.session.add(user)
            db.session.commit()
            
            # Then create linguist profile
            linguist = Linguist()
            linguist.user_id = user_id
            linguist.name = user.name
            linguist.languages = f"EN, {random.choice(['ES', 'FR', 'DE', 'IT', 'PT'])}"
            linguist.specialties = random.choice(['Legal', 'Medical', 'Technical', 'Marketing', 'General'])
            linguist.speed_score = random.randint(70, 95)
            linguist.quality_score = random.randint(70, 95)
            linguist.current_load = random.choice(['Low', 'Medium', 'High'])
            linguist.organization_id = org_id
            
            db.session.add(linguist)
            db.session.commit()
            linguists.append(linguist)
        
        # Create sample projects
        content_types = ['Legal', 'Medical', 'Technical', 'Marketing', 'General']
        statuses = ['Not Started', 'In Progress', 'Under Review', 'Completed']
        risk_statuses = ['Low Risk', 'Medium Risk', 'High Risk', None]
        
        for i in range(10):
            start_date = datetime.now() - timedelta(days=random.randint(0, 30))
            due_date = start_date + timedelta(days=random.randint(7, 30))
            
            initial_words = random.randint(1000, 10000)
            translated_words = random.randint(0, initial_words)
            
            risk_status = random.choice(risk_statuses)
            risk_reason = None
            recommendation = None
            
            if risk_status:
                risk_reason = f'This project has {risk_status.lower()} factors based on timeline and complexity.'
                recommendation = 'Consider allocating additional resources.' if risk_status == 'High Risk' else 'Monitor progress regularly.'
            
            project = Project()
            project.client_name = fake.company()
            project.project_name = f'Project {fake.word().capitalize()}'
            project.language_pair = f"EN-{random.choice(['ES', 'FR', 'DE', 'IT', 'PT'])}"
            project.content_type = random.choice(content_types)
            project.start_date = start_date
            project.due_date = due_date
            project.initial_word_count = initial_words
            project.translated_words = translated_words
            project.assigned_linguist_id = random.choice(linguists).id if linguists else None
            project.status = random.choice(statuses)
            project.gpo_risk_status = risk_status
            project.gpo_risk_reason = risk_reason
            project.gpo_recommendation = recommendation
            project.source_file_path = None
            project.organization_id = org_id
            project.created_by = admin_id
            
            db.session.add(project)
        
        db.session.commit()
        print('Database initialized successfully!')

if __name__ == '__main__':
    init_db() 