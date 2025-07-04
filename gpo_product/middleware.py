from flask import request, g, current_app, session
from functools import wraps
import json
import logging
from datetime import datetime, timedelta
from sqlalchemy import text
from database import db, AuditLog, Notification, Organization, User

def init_middleware(app):
    """Initialize all middleware for the application"""
    
    @app.before_request
    def set_organization_context():
        """Set organization context for multi-tenancy"""
        if hasattr(g, 'user') and g.user and g.user.is_authenticated:
            org_id = g.user.organization_id
            
            # Set the PostgreSQL session variable for row-level security
            if org_id:
                try:
                    db.session.execute(text(f"SET app.current_organization_id = '{org_id}'"))
                except Exception as e:
                    current_app.logger.warning(f"Could not set organization context: {e}")
        else:
            # For public pages, don't set an organization context
            pass

    @app.before_request
    def check_user_status():
        """Check if user account is active and not locked"""
        if hasattr(g, 'user') and g.user and g.user.is_authenticated:
            # Check if user is locked
            if g.user.locked_until and g.user.locked_until > datetime.utcnow():
                from flask_login import logout_user
                logout_user()
                return {'error': 'Account is temporarily locked due to failed login attempts'}, 403
            
            # Check if user is active
            if g.user.status != 'active':
                from flask_login import logout_user
                logout_user()
                return {'error': 'Account is not active'}, 403

    @app.after_request
    def audit_request(response):
        """Log all requests for audit purposes"""
        if hasattr(g, 'user') and g.user and g.user.is_authenticated:
            try:
                # Don't log static files or health checks
                if not request.path.startswith('/static') and request.path != '/health':
                    audit_log = AuditLog()
                    audit_log.organization_id = g.user.organization_id
                    audit_log.user_id = g.user.id
                    audit_log.action = request.method
                    audit_log.entity_type = 'request'
                    audit_log.entity_id = request.path
                    audit_log.details = json.dumps({
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code,
                        'user_agent': request.headers.get('User-Agent', ''),
                        'ip_address': request.remote_addr
                    })
                    audit_log.ip_address = request.remote_addr
                    audit_log.user_agent = request.headers.get('User-Agent', '')
                    audit_log.created_at = datetime.utcnow()
                    db.session.add(audit_log)
                    db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Failed to create audit log: {e}")
        
        return response

def require_role(roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or not g.user or not g.user.is_authenticated:
                return {'error': 'Authentication required'}, 401
            
            if not isinstance(roles, list):
                roles_list = [roles]
            else:
                roles_list = roles
            
            if g.user.role not in roles_list:
                return {'error': 'Insufficient permissions'}, 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_organization_access():
    """Decorator to ensure user has access to the organization"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'user') or not g.user or not g.user.is_authenticated:
                return {'error': 'Authentication required'}, 401
            
            # Check if organization is active
            organization = Organization.query.get(g.user.organization_id)
            if not organization or organization.subscription_status != 'active':
                return {'error': 'Organization subscription is not active'}, 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_requests=100, window=3600):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if hasattr(g, 'user') and g.user and g.user.is_authenticated:
                # Check rate limit for authenticated users
                key = f"rate_limit:{g.user.id}"
                # This is a simplified implementation - in production, use Redis
                # For now, we'll just allow all requests
                pass
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def create_notification(user_id, title, message, notification_type='info', action_url=None):
    """Helper function to create notifications"""
    try:
        notification = Notification()
        notification.organization_id = g.user.organization_id
        notification.user_id = user_id
        notification.title = title
        notification.message = message
        notification.notification_type = notification_type
        notification.action_url = action_url
        notification.created_at = datetime.utcnow()
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        current_app.logger.error(f"Failed to create notification: {e}")
        return None

def log_user_activity(action, entity_type, entity_id=None, details=None):
    """Helper function to log user activities"""
    try:
        audit_log = AuditLog()
        audit_log.organization_id = g.user.organization_id
        audit_log.user_id = g.user.id
        audit_log.action = action
        audit_log.entity_type = entity_type
        audit_log.entity_id = entity_id
        audit_log.details = json.dumps(details) if details else None
        audit_log.ip_address = request.remote_addr
        audit_log.user_agent = request.headers.get('User-Agent', '')
        audit_log.created_at = datetime.utcnow()
        db.session.add(audit_log)
        db.session.commit()
        return audit_log
    except Exception as e:
        current_app.logger.error(f"Failed to log user activity: {e}")
        return None

def check_organization_limits():
    """Check if organization has reached its limits"""
    if not hasattr(g, 'user') or not g.user:
        return False
    
    organization = Organization.query.get(g.user.organization_id)
    if not organization:
        return False
    
    # Check user limit
    user_count = User.query.filter_by(organization_id=g.user.organization_id).count()
    if user_count >= organization.max_users:
        return {'limit': 'users', 'current': user_count, 'max': organization.max_users}
    
    # Check project limit
    from database import Project
    project_count = Project.query.filter_by(organization_id=g.user.organization_id).count()
    if project_count >= organization.max_projects:
        return {'limit': 'projects', 'current': project_count, 'max': organization.max_projects}
    
    return False 