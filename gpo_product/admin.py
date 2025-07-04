from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import uuid
import json
from sqlalchemy import text

# Create a blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Middleware to ensure only admins can access these routes
@admin_bp.before_request
def check_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('dashboard'))

@admin_bp.route('/user-management')
@login_required
def user_management():
    """User management page for admins"""
    from database import db, User
    
    # Get all users for the current organization
    users = User.query.filter_by(organization_id=current_user.organization_id).all()
    
    # Get organization details
    from database import Organization
    organization = Organization.query.get(current_user.organization_id)
    
    # If organization doesn't exist, create a default one
    if organization is None and current_user.organization_id:
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
    
    return render_template(
        'admin/user_management.html',
        users=users,
        organization=organization,
        current_year=current_year
    )

@admin_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create a new user in the organization"""
    if request.method == 'POST':
        from database import db, User, Organization
        
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role')
        password = request.form.get('password')
        
        # Validate input
        if not name or not email or not role or not password:
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('admin.create_user'))
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('admin.create_user'))
        
        # Check user limits
        organization = Organization.query.get(current_user.organization_id)
        current_user_count = User.query.filter_by(organization_id=current_user.organization_id).count()
        
        # Set default max users if organization is None
        max_users = 5
        if organization:
            max_users = organization.max_users or 5
            
        if current_user_count >= max_users:
            flash(f'You have reached your user limit ({max_users}). Please upgrade your subscription to add more users.', 'error')
            return redirect(url_for('admin.user_management'))
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        
        # Insert the user using raw SQL with text()
        db.session.execute(
            text("""
            INSERT INTO users (id, email, name, password_hash, role, organization_id, created_at)
            VALUES (:id, :email, :name, :password_hash, :role, :organization_id, :created_at)
            """),
            {
                "id": user_id,
                "email": email,
                "name": name,
                "password_hash": password_hash,
                "role": role,
                "organization_id": current_user.organization_id,
                "created_at": datetime.utcnow()
            }
        )
        
        # If the user is a linguist, create a linguist profile
        if role == 'linguist':
            # Insert linguist profile using raw SQL with text()
            db.session.execute(
                text("""
                INSERT INTO linguists (user_id, name, languages, specialties, speed_score, quality_score, current_load, organization_id, created_at)
                VALUES (:user_id, :name, :languages, :specialties, :speed_score, :quality_score, :current_load, :organization_id, :created_at)
                """),
                {
                    "user_id": user_id,
                    "name": name,
                    "languages": 'EN',  # Default language
                    "specialties": 'General',  # Default specialty
                    "speed_score": 80,  # Default score
                    "quality_score": 80,  # Default score
                    "current_load": 'Low',  # Default load
                    "organization_id": current_user.organization_id,
                    "created_at": datetime.utcnow()
                }
            )
        
        # Create audit log
        log_entry = {
            'organization_id': current_user.organization_id,
            'user_id': current_user.id,
            'action': 'create_user',
            'entity_type': 'user',
            'entity_id': user_id,
            'details': json.dumps({
                'name': name,
                'email': email,
                'role': role
            }),
            'created_at': datetime.utcnow()
        }
        
        db.session.execute(
            text("""
            INSERT INTO audit_logs (organization_id, user_id, action, entity_type, entity_id, details, created_at)
            VALUES (:organization_id, :user_id, :action, :entity_type, :entity_id, :details, :created_at)
            """),
            log_entry
        )
        
        db.session.commit()
        
        flash(f'User {name} created successfully', 'success')
        return redirect(url_for('admin.user_management'))
    
    # Get the current year for the footer
    current_year = datetime.now().year
    
    return render_template(
        'admin/create_user.html',
        current_year=current_year
    )

@admin_bp.route('/edit-user/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit an existing user"""
    from database import db, User, Linguist
    
    # Get the user
    user = User.query.filter_by(id=user_id, organization_id=current_user.organization_id).first_or_404()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        role = request.form.get('role')
        
        # Validate input
        if not name or not role:
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        # Update user
        user.name = name
        
        # If role is changing, handle the change
        if user.role != role:
            old_role = user.role
            user.role = role
            
            # If changing to linguist, create a linguist profile if it doesn't exist
            if role == 'linguist':
                # Check if linguist profile exists
                linguist = Linguist.query.filter_by(user_id=user_id).first()
                
                if not linguist:
                    # Create linguist profile
                    db.session.execute(
                        text("""
                        INSERT INTO linguists (user_id, name, languages, specialties, speed_score, quality_score, current_load, organization_id, created_at)
                        VALUES (:user_id, :name, :languages, :specialties, :speed_score, :quality_score, :current_load, :organization_id, :created_at)
                        """),
                        {
                            "user_id": user_id,
                            "name": name,
                            "languages": 'EN',  # Default language
                            "specialties": 'General',  # Default specialty
                            "speed_score": 80,  # Default score
                            "quality_score": 80,  # Default score
                            "current_load": 'Low',  # Default load
                            "organization_id": current_user.organization_id,
                            "created_at": datetime.utcnow()
                        }
                    )
        
        # Create audit log
        log_entry = {
            'organization_id': current_user.organization_id,
            'user_id': current_user.id,
            'action': 'edit_user',
            'entity_type': 'user',
            'entity_id': user_id,
            'details': json.dumps({
                'name': name,
                'role': role
            }),
            'created_at': datetime.utcnow()
        }
        
        db.session.execute(
            text("""
            INSERT INTO audit_logs (organization_id, user_id, action, entity_type, entity_id, details, created_at)
            VALUES (:organization_id, :user_id, :action, :entity_type, :entity_id, :details, :created_at)
            """),
            log_entry
        )
        
        db.session.commit()
        
        flash(f'User {name} updated successfully', 'success')
        return redirect(url_for('admin.user_management'))
    
    # Get the current year for the footer
    current_year = datetime.now().year
    
    return render_template(
        'admin/edit_user.html',
        user=user,
        current_year=current_year
    )

@admin_bp.route('/delete-user/<user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user"""
    from database import db, User
    
    # Get the user
    user = User.query.filter_by(id=user_id, organization_id=current_user.organization_id).first_or_404()
    
    # Cannot delete yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin.user_management'))
    
    # Cannot delete the last admin
    if user.role == 'admin':
        # Count admins
        admin_count = User.query.filter_by(organization_id=current_user.organization_id, role='admin').count()
        
        if admin_count <= 1:
            flash('Cannot delete the last admin user', 'error')
            return redirect(url_for('admin.user_management'))
    
    # Create audit log before deletion
    log_entry = {
        'organization_id': current_user.organization_id,
        'user_id': current_user.id,
        'action': 'delete_user',
        'entity_type': 'user',
        'entity_id': user_id,
        'details': json.dumps({
            'name': user.name,
            'email': user.email,
            'role': user.role
        }),
        'created_at': datetime.utcnow()
    }
    
    db.session.execute(
        text("""
        INSERT INTO audit_logs (organization_id, user_id, action, entity_type, entity_id, details, created_at)
        VALUES (:organization_id, :user_id, :action, :entity_type, :entity_id, :details, :created_at)
        """),
        log_entry
    )
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.name} deleted successfully', 'success')
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/organization-settings', methods=['GET', 'POST'])
@login_required
def organization_settings():
    """Organization settings page for admins"""
    from database import db, Organization
    
    # Get organization details
    organization = Organization.query.get(current_user.organization_id)
    
    # If organization doesn't exist, create a default one
    if organization is None and current_user.organization_id:
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
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        
        if not name:
            flash('Organization name is required', 'error')
            return redirect(url_for('admin.organization_settings'))
        
        try:
            # If organization still doesn't exist, create it now
            if organization is None:
                organization = Organization()
                organization.id = current_user.organization_id
                organization.subscription_tier = 'free'
                organization.subscription_status = 'active'
                organization.max_users = 5
                organization.max_projects = 10
                organization.created_at = datetime.utcnow()
                db.session.add(organization)
            
            # Update organization name
            organization.name = name
            organization.updated_at = datetime.utcnow()
            
            # Create audit log
            log_entry = {
                'organization_id': current_user.organization_id,
                'user_id': current_user.id,
                'action': 'update_organization',
                'entity_type': 'organization',
                'entity_id': organization.id if organization else current_user.organization_id,
                'details': json.dumps({
                    'name': name
                }),
                'created_at': datetime.utcnow()
            }
            
            db.session.execute(
                text("""
                INSERT INTO audit_logs (organization_id, user_id, action, entity_type, entity_id, details, created_at)
                VALUES (:organization_id, :user_id, :action, :entity_type, :entity_id, :details, :created_at)
                """),
                log_entry
            )
            
            db.session.commit()
            
            flash('Organization settings updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating organization: {str(e)}")
            flash('An error occurred while updating organization settings', 'error')
        
        return redirect(url_for('admin.organization_settings'))
    
    # Get the current year for the footer
    current_year = datetime.now().year
    
    return render_template(
        'admin/organization_settings.html',
        organization=organization,
        current_year=current_year
    )

@admin_bp.route('/subscription', methods=['GET', 'POST'])
@login_required
def subscription():
    """Subscription management page for admins"""
    from database import db, Organization, User, Project
    
    # Get organization details
    organization = Organization.query.get(current_user.organization_id)
    
    # If organization doesn't exist, create a default one
    if organization is None and current_user.organization_id:
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
    
    if request.method == 'POST':
        # Get form data
        tier = request.form.get('tier')
        
        if not tier or tier not in ['free', 'basic', 'professional', 'enterprise']:
            flash('Invalid subscription tier selected', 'error')
            return redirect(url_for('admin.subscription'))
        
        try:
            # If organization still doesn't exist, create it now
            if organization is None:
                organization = Organization()
                organization.id = current_user.organization_id
                organization.name = f"{current_user.name}'s Organization"
                organization.subscription_status = 'active'
                organization.created_at = datetime.utcnow()
                db.session.add(organization)
            
            # Update subscription tier
            organization.subscription_tier = tier
            
            # Set limits based on tier
            if tier == 'free':
                organization.max_users = 5
                organization.max_projects = 10
            elif tier == 'basic':
                organization.max_users = 10
                organization.max_projects = 50
            elif tier == 'professional':
                organization.max_users = 25
                organization.max_projects = 200
            elif tier == 'enterprise':
                organization.max_users = 100
                organization.max_projects = 1000
            
            organization.subscription_start_date = datetime.utcnow()
            organization.subscription_end_date = datetime.utcnow() + timedelta(days=365)  # 1 year subscription
            organization.updated_at = datetime.utcnow()
            
            # Create audit log
            log_entry = {
                'organization_id': current_user.organization_id,
                'user_id': current_user.id,
                'action': 'update_subscription',
                'entity_type': 'organization',
                'entity_id': organization.id if organization else current_user.organization_id,
                'details': json.dumps({
                    'tier': tier,
                    'max_users': organization.max_users,
                    'max_projects': organization.max_projects
                }),
                'created_at': datetime.utcnow()
            }
            
            db.session.execute(
                text("""
                INSERT INTO audit_logs (organization_id, user_id, action, entity_type, entity_id, details, created_at)
                VALUES (:organization_id, :user_id, :action, :entity_type, :entity_id, :details, :created_at)
                """),
                log_entry
            )
            
            db.session.commit()
            
            flash(f'Subscription updated to {tier.capitalize()} tier successfully', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating subscription: {str(e)}")
            flash('An error occurred while updating subscription', 'error')
        
        return redirect(url_for('admin.subscription'))
    
    # Get subscription information
    subscription = {}
    usage = {}
    
    if organization:
        subscription = {
            'tier': organization.subscription_tier,
            'status': organization.subscription_status,
            'start_date': organization.subscription_start_date,
            'end_date': organization.subscription_end_date,
            'max_users': organization.max_users or 5,
            'max_projects': organization.max_projects or 10
        }
        
        # Get usage information
        user_count = User.query.filter_by(organization_id=current_user.organization_id).count()
        project_count = Project.query.filter_by(organization_id=current_user.organization_id).count()
        
        # Calculate percentages safely
        max_users = organization.max_users or 5
        max_projects = organization.max_projects or 10
        
        users_percentage = (user_count / max_users * 100) if max_users > 0 else 0
        projects_percentage = (project_count / max_projects * 100) if max_projects > 0 else 0
        
        usage = {
            'users': user_count,
            'projects': project_count,
            'users_percentage': min(users_percentage, 100),  # Cap at 100%
            'projects_percentage': min(projects_percentage, 100)  # Cap at 100%
        }
    else:
        # Default values if organization is None
        subscription = {
            'tier': 'free',
            'status': 'inactive',
            'start_date': None,
            'end_date': None,
            'max_users': 5,
            'max_projects': 10
        }
        
        usage = {
            'users': 0,
            'projects': 0,
            'users_percentage': 0,
            'projects_percentage': 0
        }
    
    # Get the current year for the footer
    current_year = datetime.now().year
    
    return render_template(
        'admin/subscription.html',
        organization=organization,
        subscription=subscription,
        usage=usage,
        current_plan=subscription['tier'],
        current_year=current_year
    )

def init_admin(app):
    """Initialize admin routes for the Flask app"""
    app.register_blueprint(admin_bp) 