from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Create a single SQLAlchemy instance
db = SQLAlchemy()

# Always load the root .env file
root_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
print(f"[DEBUG] Loading .env from: {root_env_path}")
load_dotenv(dotenv_path=root_env_path, override=True)

def init_database(app):
    """Initialize the database with the Flask app"""
    # Get database credentials from environment variables
    SUPABASE_PASSWORD = os.getenv('SUPABASE_PASSWORD', 'UCOXZibz5OLgTofg')
    SUPABASE_HOST = os.getenv('SUPABASE_HOST', 'db.dbbpghthgnwozewmlzes.supabase.co')
    SUPABASE_PORT = os.getenv('SUPABASE_PORT', '5432')
    SUPABASE_DB = os.getenv('SUPABASE_DB', 'postgres')
    SUPABASE_USER = os.getenv('SUPABASE_USER', 'postgres')

    print(f"[DEBUG] DB HOST: {SUPABASE_HOST}")
    print(f"[DEBUG] DB PORT: {SUPABASE_PORT}")
    print(f"[DEBUG] DB USER: {SUPABASE_USER}")
    print(f"[DEBUG] DB PASSWORD: {SUPABASE_PASSWORD}")

    # Only use the provided host
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}"
    except Exception as e:
        print(f"❌ Failed to connect to {SUPABASE_HOST}: {str(e)}")
        # Fall back to SQLite
        sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gpo.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{sqlite_path}"
        print(f"⚠️ Falling back to SQLite database at {sqlite_path}")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Create all tables
    db.init_app(app)
    with app.app_context():
        try:
            db.engine.connect()
            print(f"✅ Connected to database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        except Exception as e:
            print(f"❌ Could not connect to database: {e}")
        
        # Check if tables exist, create them if they don't
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            print("🔄 Creating all tables with correct schema...")
            db.create_all()
            print("✅ Database tables created")
        else:
            print("✅ Database tables already exist")
            
            # Add missing columns to organizations table
            try:
                missing_columns = [
                    ('domain', 'TEXT'),
                    ('subscription_tier', 'TEXT DEFAULT \'free\''),
                    ('subscription_status', 'TEXT DEFAULT \'active\''),
                    ('subscription_start_date', 'TIMESTAMP WITHOUT TIME ZONE'),
                    ('subscription_end_date', 'TIMESTAMP WITHOUT TIME ZONE'),
                    ('billing_email', 'TEXT'),
                    ('max_users', 'INTEGER DEFAULT 5'),
                    ('max_projects', 'INTEGER DEFAULT 10'),
                    ('max_storage_gb', 'INTEGER DEFAULT 1'),
                    ('features_enabled', 'TEXT DEFAULT \'basic\''),
                    ('settings', 'TEXT DEFAULT \'{}\''),
                    ('api_key', 'VARCHAR(64)'),
                    ('updated_at', 'TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()')
                ]
                
                for column_name, column_type in missing_columns:
                    try:
                        db.session.execute(db.text(f"ALTER TABLE organizations ADD COLUMN IF NOT EXISTS {column_name} {column_type}"))
                    except Exception as e:
                        print(f"⚠️ Could not add column {column_name}: {e}")
                
                db.session.commit()
                print("✅ Organizations table schema updated")
            except Exception as e:
                print(f"⚠️ Could not update organizations schema: {e}")
            
            # Add missing columns to users table
            try:
                missing_user_columns = [
                    ('status', 'TEXT DEFAULT \'active\''),
                    ('login_count', 'INTEGER DEFAULT 0'),
                    ('failed_login_attempts', 'INTEGER DEFAULT 0'),
                    ('locked_until', 'TIMESTAMP WITHOUT TIME ZONE'),
                    ('timezone', 'TEXT DEFAULT \'UTC\''),
                    ('language', 'TEXT DEFAULT \'en\''),
                    ('updated_at', 'TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()')
                ]
                
                for column_name, column_type in missing_user_columns:
                    try:
                        db.session.execute(db.text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column_name} {column_type}"))
                    except Exception as e:
                        print(f"⚠️ Could not add column {column_name}: {e}")
                
                db.session.commit()
                print("✅ Users table schema updated")
            except Exception as e:
                print(f"⚠️ Could not update users schema: {e}")
            
            # Verify that the project_documents table has the correct schema
            try:
                # Check if project_documents.project_id is the correct type
                result = db.session.execute(db.text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'project_documents' 
                    AND column_name = 'project_id'
                """)).fetchone()
                
                if result and result[1] != 'character varying':
                    print("🔄 Fixing project_documents schema...")
                    # Drop and recreate the table with correct schema
                    db.session.execute(db.text("DROP TABLE IF EXISTS project_documents CASCADE"))
                    db.session.commit()
                    db.create_all()
                    print("✅ Project documents table recreated with correct schema")
                else:
                    print("✅ Project documents table has correct schema")
            except Exception as e:
                print(f"⚠️ Could not verify schema: {e}")
        
        # Add missing columns to projects table
        try:
            # Check if source_lang column exists
            result = db.session.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'projects' 
                AND column_name = 'source_lang'
            """)).fetchone()
            
            if not result:
                print("🔄 Adding missing columns to projects table...")
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN source_lang TEXT"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN target_lang TEXT"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN desired_deadline DATE"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN selected_linguist_id_for_planning VARCHAR(36)"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN ai_overall_risk_status VARCHAR(50)"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN ai_risk_reason TEXT"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN ai_document_complexity VARCHAR(50)"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN ai_key_challenges TEXT"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN ai_sensitive_data_alert_summary TEXT"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN ai_recommended_linguist_profile_text TEXT"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN ai_optimal_team_size VARCHAR(10)"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN ai_deadline_fit_assessment TEXT"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN ai_strategic_recommendations TEXT"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN ai_analysis_timestamp TIMESTAMP"))
                db.session.execute(db.text("ALTER TABLE projects ADD COLUMN local_analysis_status VARCHAR(50) DEFAULT 'Pending Local Analysis'"))
                print("✅ Projects table schema updated")
            else:
                print("✅ Projects table has correct schema")
        except Exception as e:
            print(f"⚠️ Could not update projects schema: {e}")
        
        # Commit any pending changes
        db.session.commit()

# Define models
class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.Text, nullable=False)
    domain = db.Column(db.Text, nullable=True)  # Custom domain for branding
    subscription_tier = db.Column(db.Text, default='free')  # free, basic, professional, enterprise
    subscription_status = db.Column(db.Text, default='active')  # active, inactive, suspended, cancelled
    subscription_start_date = db.Column(db.DateTime)
    subscription_end_date = db.Column(db.DateTime)
    billing_email = db.Column(db.Text, nullable=True)
    max_users = db.Column(db.Integer, default=5)
    max_projects = db.Column(db.Integer, default=10)
    max_storage_gb = db.Column(db.Integer, default=1)  # Storage limit in GB
    features_enabled = db.Column(db.Text, default='basic')  # JSON string of enabled features
    settings = db.Column(db.Text, default='{}')  # JSON string of organization settings
    api_key = db.Column(db.String(64), unique=True, nullable=True)  # API key for Local Brain authentication
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False)  # admin, project_manager, linguist, client
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Text, default='active')  # active, inactive, suspended
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    timezone = db.Column(db.Text, default='UTC')
    language = db.Column(db.Text, default='en')
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
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_name = db.Column(db.Text, nullable=False)
    project_name = db.Column(db.Text, nullable=False)
    source_lang = db.Column(db.Text, nullable=False)
    target_lang = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.Text, nullable=False)
    desired_deadline = db.Column(db.Date, nullable=False)
    selected_linguist_id_for_planning = db.Column(db.String(36), db.ForeignKey('linguist_profiles.id'), nullable=True)
    
    # AI Analysis Results (God PM Blueprint)
    ai_overall_risk_status = db.Column(db.String(50), nullable=True)  # Critical, High, Medium, Low, On Track
    ai_risk_reason = db.Column(db.Text, nullable=True)
    ai_document_complexity = db.Column(db.String(50), nullable=True)  # Low, Medium, High, Very High
    ai_key_challenges = db.Column(db.Text, nullable=True)
    ai_sensitive_data_alert_summary = db.Column(db.Text, nullable=True)
    ai_recommended_linguist_profile_text = db.Column(db.Text, nullable=True)
    ai_optimal_team_size = db.Column(db.String(10), nullable=True)  # 1, 2, 3+
    ai_deadline_fit_assessment = db.Column(db.Text, nullable=True)
    ai_strategic_recommendations = db.Column(db.Text, nullable=True)
    ai_analysis_timestamp = db.Column(db.DateTime, nullable=True)
    local_analysis_status = db.Column(db.String(50), default='Pending Local Analysis')  # Pending Local Analysis, Analysis Complete, Error in Local Analysis
    
    # Legacy fields (keeping for compatibility)
    language_pair = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    initial_word_count = db.Column(db.Integer, nullable=True)
    translated_words = db.Column(db.Integer, nullable=True)
    assigned_linguist_id = db.Column(db.BigInteger, db.ForeignKey('linguists.id'), nullable=True)
    status = db.Column(db.Text, nullable=True)
    gpo_risk_status = db.Column(db.Text, nullable=True)
    gpo_risk_reason = db.Column(db.Text, nullable=True)
    gpo_recommendation = db.Column(db.Text, nullable=True)
    source_file_path = db.Column(db.Text, nullable=True)
    
    # Relationships
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    assigned_linguist = db.relationship('Linguist', backref=db.backref('projects', lazy=True))
    organization = db.relationship('Organization', backref=db.backref('projects', lazy=True))
    creator = db.relationship('User', backref=db.backref('created_projects', lazy=True))
    selected_linguist = db.relationship('LinguistProfile', backref=db.backref('planning_projects', lazy=True))

class ProjectDocument(db.Model):
    __tablename__ = 'project_documents'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    project_id = db.Column(db.String(36), db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    file_name = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Text, nullable=False, default='Uploaded')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    project = db.relationship('Project', backref=db.backref('documents', lazy=True))

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.Text, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref=db.backref('password_resets', lazy=True))

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'))
    action = db.Column(db.Text, nullable=False)  # create, update, delete, login, etc.
    entity_type = db.Column(db.Text, nullable=False)  # user, project, linguist, etc.
    entity_id = db.Column(db.Text, nullable=True)  # ID of the affected entity
    details = db.Column(db.Text, nullable=True)  # JSON string with additional details
    ip_address = db.Column(db.Text, nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    organization = db.relationship('Organization', backref=db.backref('audit_logs', lazy=True))
    user = db.relationship('User', backref=db.backref('audit_actions', lazy=True))

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.Text, nullable=False)  # info, warning, error, success
    read = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.Text, nullable=True)  # URL to navigate to when clicked
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    organization = db.relationship('Organization', backref=db.backref('notifications', lazy=True))
    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

class LinguistProfile(db.Model):
    __tablename__ = 'linguist_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    internal_id = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=True)
    specializations = db.Column(db.Text, nullable=True)  # Comma-separated string
    source_languages = db.Column(db.Text, nullable=False)  # Comma-separated string
    target_languages = db.Column(db.Text, nullable=False)  # Comma-separated string
    quality_rating = db.Column(db.String(100), nullable=True)
    general_capacity_words_per_day = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), default='Active')  # Active, Inactive, On Leave
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = db.relationship('Organization', backref=db.backref('linguist_profiles', lazy=True))
    
    # Indexes for efficient lookup
    __table_args__ = (
        db.Index('idx_linguist_org_internal', 'organization_id', 'internal_id'),
        db.Index('idx_linguist_organization', 'organization_id'),
        db.Index('idx_linguist_status', 'status'),
    ) 