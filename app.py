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
                    # Save file to dummy_docs directory
                    filename = f"{project_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
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
                    with open(file_path, 'r', encoding='utf-8') as f:
                        document_content = f.read()
                    
                    # Analyze document
                    document_analysis = simulate_document_analysis(document_content, content_type)
                    
                    # Get available linguists for assessment
                    available_linguists = Linguist.query.filter_by(current_load='Low').first()
                    
                    # Assess project risks
                    risk_status, risk_reason, recommendation = gpo_assess_project(
                        project, available_linguists, document_analysis
                    )
                    
                    # Update project with GPO results
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
        
        # Read the source file
        file_path = os.path.join(current_app.root_path, project.source_file_path)
        
        if not os.path.exists(file_path):
            flash('Source document not found', 'error')
            return redirect(url_for('project_detail', project_id=project_id))
        
        with open(file_path, 'r', encoding='utf-8') as f:
            document_content = f.read()
        
        # Analyze document
        document_analysis = simulate_document_analysis(document_content, project.content_type)
        
        # Get linguist data
        linguist_data = project.assigned_linguist
        
        # Assess project risks
        risk_status, risk_reason, recommendation = gpo_assess_project(
            project, linguist_data, document_analysis
        )
        
        # Update project
        project.gpo_risk_status = risk_status
        project.gpo_risk_reason = risk_reason
        project.gpo_recommendation = recommendation
        
        db.session.commit()
        
        flash(f'GPO Analysis completed: {risk_status}', 'success')
        
    except Exception as e:
        flash(f'Analysis failed: {str(e)}', 'error')
    
    return redirect(url_for('project_detail', project_id=project_id))

def simulate_document_analysis(document_content, content_type):
    """Enhanced document analysis with complexity scoring and sensitive data detection"""
    
    # Complexity analysis
    sentences = re.split(r'[.!?]+', document_content)
    avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
    
    # Technical jargon detection
    technical_terms = {
        'Medical': ['diagnosis', 'prognosis', 'biopsy', 'pathology', 'symptom', 'treatment', 'medication', 'dosage', 'contraindication', 'adverse effect'],
        'Legal': ['whereas', 'hereby', 'hereinafter', 'party', 'plaintiff', 'defendant', 'jurisdiction', 'liability', 'indemnification', 'breach'],
        'Technical': ['algorithm', 'protocol', 'interface', 'implementation', 'deployment', 'configuration', 'optimization', 'integration'],
        'Financial': ['revenue', 'expenditure', 'liability', 'asset', 'equity', 'depreciation', 'amortization', 'consolidation']
    }
    
    jargon_count = 0
    detected_terms = []
    if content_type in technical_terms:
        for term in technical_terms[content_type]:
            if re.search(r'\b' + re.escape(term) + r'\b', document_content, re.IGNORECASE):
                jargon_count += 1
                detected_terms.append(term)
    
    # Complexity scoring
    complexity_score = 'Low'
    if avg_sentence_length > 25 or jargon_count > 5:
        complexity_score = 'High'
    elif avg_sentence_length > 15 or jargon_count > 2:
        complexity_score = 'Medium'
    
    # Sensitive data detection
    sensitive_patterns = {
        'Medical PHI': [
            r'\bpatient\s+id\b', r'\bPHI\b', r'\bdiagnosis\b', r'\bmedication\b', 
            r'\btreatment\s+plan\b', r'\bmedical\s+record\b', r'\bHIPAA\b', 
            r'\bICD-10\b', r'\bbiopsy\b', r'\bprognosis\b'
        ],
        'Legal Confidential': [
            r'\bcontract\b', r'\bagreement\b', r'\bstipulation\b', r'\bclause\b',
            r'\bindemnification\b', r'\bproprietary\s+information\b', 
            r'\bconfidentiality\s+agreement\b', r'\blitigation\b',
            r'\battorney-client\s+privilege\b', r'\bnon-disclosure\b'
        ],
        'Military Classified': [
            r'\bclassified\b', r'\btop\s+secret\b', r'\bsecure\s+transmission\b',
            r'\bdeployment\s+strategy\b', r'\boperational\s+protocol\b',
            r'\bnational\s+security\b', r'\bweapon\s+system\b'
        ],
        'Financial PII': [
            r'\baccount\s+number\b', r'\bSSN\b', r'\bcredit\s+card\b',
            r'\bbank\s+details\b', r'\bfinancial\s+statement\b', r'\bPII\b'
        ],
        'General PII': [
            r'\bemail\s+address\b', r'\bphone\s+number\b', r'\bhome\s+address\b',
            r'\bdate\s+of\s+birth\b', r'\bsocial\s+security\s+number\b'
        ]
    }
    
    sensitive_data_flag = False
    sensitive_data_type = None
    
    for data_type, patterns in sensitive_patterns.items():
        for pattern in patterns:
            if re.search(pattern, document_content, re.IGNORECASE):
                sensitive_data_flag = True
                sensitive_data_type = data_type
                break
        if sensitive_data_flag:
            break
    
    # Terminology analysis
    terminology_flag = jargon_count > 3
    terminology_details = detected_terms[:5]  # Limit to first 5 terms
    
    return {
        'complexity_score': complexity_score,
        'sensitive_data_flag': sensitive_data_flag,
        'sensitive_data_type': sensitive_data_type,
        'terminology_flag': terminology_flag,
        'terminology_details': terminology_details,
        'avg_sentence_length': avg_sentence_length,
        'jargon_count': jargon_count
    }

def gpo_assess_project(project, linguist_data, document_analysis_results):
    """Enhanced GPO risk assessment with detailed analysis"""
    
    # If project is completed, no further action needed
    if project.status == 'Completed':
        return 'Completed', 'Project finalized.', 'No further action required.'
    
    # Initialize risk assessment
    risk_factors = []
    recommendations = []
    
    # Deadline Risk Analysis
    progress_ratio = project.translated_words / project.initial_word_count if project.initial_word_count > 0 else 0
    time_elapsed_ratio = (datetime.utcnow().date() - project.start_date).days / max((project.due_date - project.start_date).days, 1)
    days_remaining = (project.due_date - datetime.utcnow().date()).days
    
    if progress_ratio < time_elapsed_ratio * 0.7 and days_remaining < 5:
        risk_factors.append(f"Behind schedule: {project.translated_words} of {project.initial_word_count} words translated. Only {days_remaining} days remaining.")
        recommendations.append("Allocate additional linguist resources or negotiate deadline extension. Prioritize high-impact sections.")
    
    # Quality Risk Analysis
    if document_analysis_results['complexity_score'] == 'High':
        if not linguist_data or linguist_data.quality_score < 85 or project.content_type not in linguist_data.specialties:
            risk_factors.append(f"Potential quality issue: Complex content assigned to linguist with quality score {linguist_data.quality_score if linguist_data else 'N/A'} or no matching specialty.")
            recommendations.append("Initiate immediate quality review. Consider re-assigning to a more specialized/higher-rated linguist.")
    
    # Resource Risk Analysis
    if linguist_data and linguist_data.current_load == 'High' and project.initial_word_count > 10000 and project.status == 'In Progress':
        risk_factors.append(f"Linguist '{linguist_data.name}' has high current workload for a large project ({project.initial_word_count} words).")
        recommendations.append("Monitor linguist's progress closely. Be prepared to reallocate parts of the project.")
    
    # Sensitive Data Risk (Highest Priority)
    if document_analysis_results['sensitive_data_flag']:
        risk_factors.append(f"Sensitive data detected: '{document_analysis_results['sensitive_data_type']}' identified in source document.")
        recommendations.append("IMMEDIATE ACTION: Halt standard translation. Initiate secure workflow. Consult legal/compliance department.")
    
    # Terminology Risk
    if document_analysis_results['terminology_flag'] and project.content_type in ['Medical', 'Legal', 'Technical', 'Financial']:
        if not linguist_data or project.content_type not in linguist_data.specialties or linguist_data.quality_score < 90:
            risk_factors.append(f"High density of specialized terminology detected for '{project.content_type}' content.")
            recommendations.append("Ensure linguist has access to updated glossaries/TMs. Recommend a specialized terminology review step.")
    
    # Determine overall risk status
    if document_analysis_results['sensitive_data_flag']:
        risk_status = 'Critical Risk'
    elif len(risk_factors) >= 3:
        risk_status = 'High Risk'
    elif len(risk_factors) >= 2:
        risk_status = 'Medium Risk'
    elif len(risk_factors) >= 1:
        risk_status = 'Low Risk'
    else:
        risk_status = 'On Track'
    
    risk_reason = "; ".join(risk_factors) if risk_factors else "Project is proceeding as expected."
    recommendation = "; ".join(recommendations) if recommendations else "Continue monitoring. Consider proactive feedback loops with linguist."
    
    return risk_status, risk_reason, recommendation

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