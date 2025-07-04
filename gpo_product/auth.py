from flask import Blueprint, request, redirect, url_for, flash, render_template, session, current_app
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime, timedelta
import os
import json
import requests
from sqlalchemy import text

# Create a blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# Initialize LoginManager
login_manager = LoginManager()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, name, role, organization_id=None):
        self.id = id
        self.email = email
        self.name = name
        self.role = role
        self.organization_id = organization_id

    def get_id(self):
        return self.id
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_project_manager(self):
        return self.role == 'project_manager'
    
    @property
    def is_linguist(self):
        return self.role == 'linguist'
    
    @property
    def is_client(self):
        return self.role == 'client'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Query the database for the user using ORM
    from database import db, User as UserModel
    
    try:
        user = UserModel.query.get(user_id)
        if user:
            return User(
                id=str(user.id),  # type: ignore
                email=str(user.email),  # type: ignore
                name=str(user.name),  # type: ignore
                role=str(user.role),  # type: ignore
                organization_id=str(user.organization_id)  # type: ignore
            )
    except Exception as e:
        print(f"Error loading user {user_id}: {e}")
    return None

# Set up login view
@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view this page.', 'error')
    return redirect(url_for('auth.login'))

# Routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'error')
            return render_template('login.html')
        
        # Query the database for the user using ORM
        from database import db, User as UserModel
        
        user = UserModel.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(User(
                id=user.id,
                email=user.email,
                name=user.name,
                role=user.role,
                organization_id=user.organization_id
            ))
            
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Redirect to the page the user was trying to access
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard')
            
            return redirect(next_page)
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not name or not email or not password:
            flash('Please fill in all required fields', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        from database import db, User as UserModel, Organization as OrganizationModel
        
        existing_user = UserModel.query.filter_by(email=email).first()
        
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        
        # For the initial user, make them an admin of a new organization
        organization_id = str(uuid.uuid4())
        
        try:
            print(f"[DEBUG] Creating organization: {organization_id}")
            print(f"[DEBUG] Organization name: {name}'s Organization")
            
            # Create organization using ORM
            organization = OrganizationModel(
                id=organization_id,  # type: ignore
                name=f"{name}'s Organization"  # type: ignore
            )
            db.session.add(organization)
            
            print(f"[DEBUG] Creating user: {user_id}")
            print(f"[DEBUG] User email: {email}")
            
            # Create user using ORM
            user = UserModel(
                id=user_id,  # type: ignore
                email=email,  # type: ignore
                name=name,  # type: ignore
                password_hash=password_hash,  # type: ignore
                role="admin",  # type: ignore
                organization_id=organization_id  # type: ignore
            )
            db.session.add(user)
            
            db.session.commit()
            
            # Log in the new user
            user = User(
                id=user_id,
                email=email,
                name=name,
                role="admin",
                organization_id=organization_id
            )
            login_user(user)
            
            flash('Registration successful! Welcome to GPO.', 'success')
            return redirect(url_for('dashboard'))
        
        except Exception as e:
            db.session.rollback()
            print(f"[DEBUG] EXCEPTION CAUGHT: {str(e)}")
            print(f"[DEBUG] Exception type: {type(e)}")
            current_app.logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration', 'error')
    
    return render_template('register.html')

@auth_bp.route('/profile')
@login_required
def profile():
    # Get organization details
    from database import Organization
    organization = Organization.query.get(current_user.organization_id)
    
    # If organization doesn't exist, create a default one
    if organization is None and current_user.organization_id:
        from database import db
        try:
            # Create a default organization
            organization = Organization()
            organization.id = current_user.organization_id
            organization.name = f"{current_user.name}'s Organization"
            organization.subscription_tier = 'free'
            organization.subscription_status = 'active'
            organization.max_users = 5
            organization.max_projects = 10
            organization.created_at = datetime.utcnow()
            organization.updated_at = datetime.utcnow()
            
            db.session.add(organization)
            db.session.commit()
            
            flash('A default organization has been created for you.', 'info')
        except Exception as e:
            current_app.logger.error(f"Error creating default organization: {str(e)}")
            flash('Could not create a default organization. Some features may be limited.', 'warning')
    
    # Get the current year for the footer
    current_year = datetime.now().year
    
    return render_template('profile.html', organization=organization, current_year=current_year)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('Please fill in all fields', 'error')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('auth.profile'))
    
    # Check current password
    from database import db
    
    result = db.session.execute(
        text("SELECT password_hash FROM users WHERE id = :user_id"),
        {"user_id": current_user.id}
    ).fetchone()
    
    if result and check_password_hash(result[0], current_password):
        # Update password
        new_password_hash = generate_password_hash(new_password)
        
        db.session.execute(
            text("UPDATE users SET password_hash = :password_hash WHERE id = :user_id"),
            {"password_hash": new_password_hash, "user_id": current_user.id}
        )
        
        db.session.commit()
        
        flash('Password updated successfully', 'success')
    else:
        flash('Current password is incorrect', 'error')
    
    return redirect(url_for('auth.profile'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please provide your email address', 'error')
            return render_template('reset_password_request.html')
        
        # Check if user exists
        from database import db
        
        user = db.session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": email}
        ).fetchone()
        
        if user:
            # Generate reset token
            token = str(uuid.uuid4())
            
            # Store token in database
            db.session.execute(
                text("""
                INSERT INTO password_resets (user_id, token, created_at, expires_at)
                VALUES (:user_id, :token, :created_at, :expires_at)
                """),
                {
                    "user_id": user[0],
                    "token": token,
                    "created_at": datetime.utcnow(),
                    "expires_at": datetime.utcnow() + timedelta(hours=1)
                }
            )
            db.session.commit()
            
            # In a real application, send an email with the reset link
            # For now, just flash the token (for development purposes)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            flash(f'Password reset link: {reset_url}', 'info')
            
        # Always show the same message to prevent email enumeration
        flash('If your email is registered, you will receive a password reset link', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password_request.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Check if token is valid
    from database import db
    
    reset_info = db.session.execute(
        text("""
        SELECT user_id, expires_at FROM password_resets
        WHERE token = :token AND used = FALSE
        """),
        {"token": token}
    ).fetchone()
    
    if not reset_info or reset_info[1] < datetime.utcnow():
        flash('Invalid or expired password reset link', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Please fill in all fields', 'error')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)
        
        # Update user's password
        password_hash = generate_password_hash(password)
        
        db.session.execute(
            text("""
            UPDATE users SET password_hash = :password_hash
            WHERE id = :user_id
            """),
            {
                "password_hash": password_hash,
                "user_id": reset_info[0]
            }
        )
        
        # Mark token as used
        db.session.execute(
            text("""
            UPDATE password_resets SET used = TRUE
            WHERE token = :token
            """),
            {"token": token}
        )
        
        db.session.commit()
        
        flash('Your password has been reset successfully', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', token=token)

def init_auth(app):
    """Initialize authentication for the Flask app"""
    login_manager.init_app(app)
    app.register_blueprint(auth_bp, url_prefix='/auth') 