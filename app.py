from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import re
from dotenv import load_dotenv
from faker import Faker
import random
import socket
import sys
import fitz  # PyMuPDF
import docx
import json
import logging
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Production Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
app.config['DEBUG'] = os.getenv('FLASK_ENV') != 'production'

# Supabase PostgreSQL connection string - load from environment
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_PASSWORD = os.getenv('SUPABASE_PASSWORD')
SUPABASE_HOST = os.getenv('SUPABASE_HOST', 'db.dbbpghthgnwozewmlzes.supabase.co')
SUPABASE_PORT = os.getenv('SUPABASE_PORT', '6543')
SUPABASE_DB = os.getenv('SUPABASE_DB', 'postgres')

if SUPABASE_URL and SUPABASE_PASSWORD:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}"
else:
    # Fallback to hardcoded for development (should be removed in production)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:UCOXZibz5OLgTofg@db.dbbpghthgnwozewmlzes.supabase.co:6543/postgres"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
fake = Faker()

# Configure logging for production
if app.config['DEBUG']:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(
        filename='gpo.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )

# Load LLM API key
LLM_API_KEY = os.getenv('LLM_API_KEY')

# Initialize Gemini LLM client (if available)
llm_model = None
if genai and LLM_API_KEY:
    try:
        genai.configure(api_key=LLM_API_KEY)
        llm_model = genai.GenerativeModel('gemini-pro')
        logging.info("Gemini LLM initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize Gemini LLM: {e}")

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
    assigned_linguist_id = db.Column(db.BigInteger, db.ForeignKey('linguists.id'))
    status = db.Column(db.Text, nullable=False)
    gpo_risk_status = db.Column(db.Text)
    gpo_risk_reason = db.Column(db.Text)
    gpo_recommendation = db.Column(db.Text)
    source_file_path = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    
    # Relationship
    assigned_linguist = db.relationship('Linguist', backref='projects_assigned')

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
    projects = db.session.query(Project).options(db.joinedload(Project.assigned_linguist)).all()
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
    high_risk_projects = len([p for p in projects if p.gpo_risk_status == 'High Risk'])
    medium_risk_projects = len([p for p in projects if p.gpo_risk_status == 'Medium Risk'])
    low_risk_projects = len([p for p in projects if p.gpo_risk_status == 'Low Risk'])
    critical_risk_projects = len([p for p in projects if p.gpo_risk_status == 'Critical Risk'])

    return render_template('dashboard.html', 
                         projects=projects_dict, 
                         linguists=linguists_dict,
                         total_projects=total_projects,
                         high_risk=high_risk_projects,
                         medium_risk=medium_risk_projects,
                         low_risk=low_risk_projects,
                         critical_risk=critical_risk_projects)

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    """Create new project with file upload and GPO analysis"""
    if request.method == 'POST':
        try:
            # Get form data
            client_name = request.form['client_name']
            project_name = request.form['project_name']
            language_pair = request.form['language_pair']
            content_type = request.form['content_type']
            due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
            initial_word_count = int(request.form['initial_word_count'])
            
            # Handle file upload
            if 'source_document' in request.files:
                file = request.files['source_document']
                if file.filename:
                    ext = os.path.splitext(file.filename)[1].lower()
                    filename = f"{project_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                    file_path = os.path.join(current_app.root_path, 'dummy_docs', filename)
                    file.save(file_path)
                    source_file_path = f"dummy_docs/{filename}"
                else:
                    source_file_path = None
            else:
                source_file_path = None
            
            # Create project
            project = Project()
            project.client_name = client_name
            project.project_name = project_name
            project.language_pair = language_pair
            project.content_type = content_type
            project.start_date = datetime.now().date()
            project.due_date = due_date
            project.initial_word_count = initial_word_count
            project.translated_words = 0
            project.assigned_linguist_id = None
            project.status = 'Pending Assignment'
            project.source_file_path = source_file_path
            
            db.session.add(project)
            db.session.commit()
            
            # Perform GPO analysis if file was uploaded
            if source_file_path and os.path.exists(file_path):
                try:
                    document_content = extract_text_from_document(file_path)
                    document_analysis = analyze_document_with_llm(document_content, content_type)
                    available_linguists = Linguist.query.filter_by(current_load='Low').first()
                    risk_status, risk_reason, recommendation = assess_project_with_llm(
                        project, available_linguists, document_analysis
                    )
                    project.gpo_risk_status = risk_status
                    project.gpo_risk_reason = risk_reason
                    project.gpo_recommendation = recommendation
                    db.session.commit()
                    flash(f'Project created successfully! GPO Analysis: {risk_status}', 'success')
                except Exception as e:
                    flash(f'Project created but GPO analysis failed: {str(e)}', 'warning')
            else:
                flash('Project created successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error creating project: {str(e)}', 'error')
            return redirect(url_for('create_project'))
    return render_template('create_project.html')

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Show detailed project information"""
    project = Project.query.get_or_404(project_id)
    linguist = project.assigned_linguist
    
    return render_template('project_detail.html', project=project, linguist=linguist)

@app.route('/project/<int:project_id>/analyze', methods=['POST'])
def analyze_project(project_id):
    """Run GPO AI analysis on a specific project"""
    try:
        project = Project.query.get_or_404(project_id)
        if not project.source_file_path:
            flash('No source document available for analysis', 'error')
            return redirect(url_for('project_detail', project_id=project_id))
        file_path = os.path.join(current_app.root_path, project.source_file_path)
        if not os.path.exists(file_path):
            flash('Source document not found', 'error')
            return redirect(url_for('project_detail', project_id=project_id))
        document_content = extract_text_from_document(file_path)
        document_analysis = analyze_document_with_llm(document_content, project.content_type)
        linguist_data = project.assigned_linguist
        risk_status, risk_reason, recommendation = assess_project_with_llm(
            project, linguist_data, document_analysis
        )
        project.gpo_risk_status = risk_status
        project.gpo_risk_reason = risk_reason
        project.gpo_recommendation = recommendation
        db.session.commit()
        flash(f'GPO Analysis completed: {risk_status}', 'success')
    except Exception as e:
        flash(f'Analysis failed: {str(e)}', 'error')
    return redirect(url_for('project_detail', project_id=project_id))

def extract_text_from_document(filepath):
    """Extract plain text from DOCX, PDF, or TXT files. OCR for scanned PDFs is out of scope."""
    try:
        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.docx':
            doc = docx.Document(filepath)
            return '\n'.join([p.text for p in doc.paragraphs])
        elif ext == '.pdf':
            text = []
            with fitz.open(filepath) as pdf:
                for page in pdf:
                    text.append(page.get_text())
            return '\n'.join(text)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        raise
    except Exception as e:
        logging.error(f"Error parsing document {filepath}: {e}")
        raise

def analyze_document_with_llm(document_content, content_type):
    """Analyze document using Gemini LLM. Returns dict with analysis results."""
    if not llm_model:
        raise RuntimeError("LLM model not initialized. Check LLM_API_KEY and dependencies.")
    prompt = f"""
You are an expert document analyst for a Project Orchestrator. Analyze the following document content, considering it is a '{content_type}' document. Provide your analysis in a JSON object with the following keys: 'complexity_score' (Low/Medium/High), 'complexity_reason', 'sensitive_data_flag' (boolean), 'sensitive_data_type' (Medical PHI/Legal Confidential/Financial PII/General PII/Military Classified/None), 'terminology_flag' (boolean), 'terminology_details' (list of up to 5-10 key terms), and 'summary'.\n\nDocument Content:\n{document_content[:4000]}\n\nJSON Output:"
    """
    try:
        response = llm_model.generate_content(prompt)
        text = response.text.strip()
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
        if json_start == -1 or json_end == -1:
            raise ValueError("No JSON object found in LLM response.")
        json_str = text[json_start:json_end]
        result = json.loads(json_str)
        logging.info(f"LLM document analysis success. Result: {result}")
        return result
    except Exception as e:
        logging.error(f"LLM document analysis failed: {e}. Raw response: {locals().get('text', '')}")
        raise

def assess_project_with_llm(project, linguist_data, document_analysis_results):
    """Assess project risks and recommendations using Gemini LLM."""
    if not llm_model:
        raise RuntimeError("LLM model not initialized. Check LLM_API_KEY and dependencies.")
    project_dict = {k: getattr(project, k) for k in project.__table__.columns.keys()}
    linguist_dict = {k: getattr(linguist_data, k) for k in linguist_data.__table__.columns.keys()} if linguist_data else {}
    prompt = f"""
You are an expert project risk assessor for a Language Service Provider. Given the following project details, assigned linguist data, and document analysis, assess the project risks and provide actionable recommendations. Prioritize risks in this order: Sensitive Data > Deadline > Quality > Resource > Terminology.\n\nProject Details: {json.dumps(project_dict)}\n\nLinguist Data: {json.dumps(linguist_dict)}\n\nDocument Analysis: {json.dumps(document_analysis_results)}\n\nReturn a JSON object with these keys: 'gpo_risk_status' ('On Track', 'Medium Risk', 'High Risk', 'Critical Risk'), 'gpo_risk_reason' (detailed, concise explanation), 'gpo_recommendation' (actionable advice).\n\nJSON Output:"
    """
    try:
        response = llm_model.generate_content(prompt)
        text = response.text.strip()
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
        if json_start == -1 or json_end == -1:
            raise ValueError("No JSON object found in LLM response.")
        json_str = text[json_start:json_end]
        result = json.loads(json_str)
        logging.info(f"LLM project assessment success. Result: {result}")
        return (
            result.get('gpo_risk_status'),
            result.get('gpo_risk_reason'),
            result.get('gpo_recommendation')
        )
    except Exception as e:
        logging.error(f"LLM project assessment failed: {e}. Raw response: {locals().get('text', '')}")
        raise

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
    """Legacy GPO AI logic to assess project risks and provide recommendations"""
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
        risk_status = "High Risk"
    elif len(risk_factors) >= 2:
        risk_status = "Medium Risk"
    elif len(risk_factors) >= 1:
        risk_status = "Low Risk"
    else:
        risk_status = "On Track"
    
    risk_reason = "; ".join(risk_factors) if risk_factors else "No significant risks identified"
    recommendation = "; ".join(recommendations) if recommendations else "Continue current approach"
    
    return risk_status, risk_reason, recommendation

def find_available_port(start_port=5005, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def ask_for_port_change(current_port):
    """Ask user if they want to use a different port"""
    print(f"\n⚠️  Port {current_port} is already in use!")
    print("This usually means another Flask app is running.")
    
    while True:
        response = input(f"Would you like to try a different port? (Y/N): ").strip().upper()
        if response in ['Y', 'YES']:
            new_port = find_available_port(current_port + 1)
            if new_port:
                print(f"✅ Found available port: {new_port}")
                return new_port
            else:
                print("❌ No available ports found in range. Please stop other Flask apps and try again.")
                return None
        elif response in ['N', 'NO']:
            print("❌ Cannot start app. Please stop the app using port {current_port} first.")
            return None
        else:
            print("Please enter Y or N.")

# Production error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if app.config['DEBUG']:
        return render_template('500.html', error=error), 500
    else:
        return render_template('500.html'), 500

if __name__ == '__main__':
    default_port = 5005
    
    # Check if default port is available
    if find_available_port(default_port, 1) is None:
        new_port = ask_for_port_change(default_port)
        if new_port is None:
            sys.exit(1)
        port_to_use = new_port
    else:
        port_to_use = default_port
    
    print(f"🚀 Starting GPO Flask app on port {port_to_use}")
    print(f"📱 Open your browser to: http://localhost:{port_to_use}")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        app.run(debug=True, port=port_to_use, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 GPO Flask app stopped.")
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        sys.exit(1)

print("Application is containerized with Docker and ready for Gunicorn deployment. Comprehensive documentation (`requirements.txt`, `Dockerfile`, `start.sh`, `README.md`, `DEPLOYMENT.md`, `API.md`, `COMPLIANCE.md`, `DEMO_SCRIPT.md`) is created, outlining production readiness and AI capabilities for sales.") 