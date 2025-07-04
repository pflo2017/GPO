from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json
import uuid
from database import db, Project, User, Organization, Linguist, AuditLog, Notification
from middleware import require_role, require_organization_access, log_user_activity, create_notification

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# API Routes

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# Project Management API
@api_bp.route('/projects', methods=['GET'])
@login_required
@require_organization_access()
def get_projects():
    """Get all projects for the organization"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        search = request.args.get('search')
        
        query = Project.query.filter_by(organization_id=current_user.organization_id)
        
        if status:
            query = query.filter(Project.status == status)
        
        if search:
            query = query.filter(
                (Project.project_name.ilike(f'%{search}%')) |
                (Project.client_name.ilike(f'%{search}%'))
            )
        
        projects = query.order_by(desc(Project.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'projects': [{
                'id': p.id,
                'client_name': p.client_name,
                'project_name': p.project_name,
                'language_pair': p.language_pair,
                'content_type': p.content_type,
                'start_date': p.start_date.isoformat() if p.start_date else None,
                'due_date': p.due_date.isoformat() if p.due_date else None,
                'initial_word_count': p.initial_word_count,
                'translated_words': p.translated_words,
                'status': p.status,
                'gpo_risk_status': p.gpo_risk_status,
                'gpo_risk_reason': p.gpo_risk_reason,
                'gpo_recommendation': p.gpo_recommendation,
                'assigned_linguist_id': p.assigned_linguist_id,
                'created_at': p.created_at.isoformat(),
                'updated_at': p.updated_at.isoformat()
            } for p in projects.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': projects.total,
                'pages': projects.pages,
                'has_next': projects.has_next,
                'has_prev': projects.has_prev
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error getting projects: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/projects', methods=['POST'])
@login_required
@require_role(['admin', 'project_manager'])
@require_organization_access()
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['client_name', 'project_name', 'language_pair', 'content_type', 'start_date', 'due_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse dates
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        if due_date < start_date:
            return jsonify({'error': 'Due date cannot be before start date'}), 400
        
        # Create project
        project = Project()
        project.client_name = data['client_name']
        project.project_name = data['project_name']
        project.language_pair = data['language_pair']
        project.content_type = data['content_type']
        project.start_date = start_date
        project.due_date = due_date
        project.initial_word_count = data.get('initial_word_count', 0)
        project.translated_words = data.get('translated_words', 0)
        project.status = data.get('status', 'Not Started')
        project.organization_id = current_user.organization_id
        project.created_by = current_user.id
        
        db.session.add(project)
        db.session.commit()
        
        # Log activity
        log_user_activity('create', 'project', str(project.id), {
            'project_name': project.project_name,
            'client_name': project.client_name
        })
        
        # Create notification for admins
        admins = User.query.filter_by(
            organization_id=current_user.organization_id,
            role='admin'
        ).all()
        
        for admin in admins:
            if admin.id != current_user.id:
                create_notification(
                    admin.id,
                    'New Project Created',
                    f'Project "{project.project_name}" has been created by {current_user.name}',
                    'info',
                    f'/project/{project.id}'
                )
        
        return jsonify({
            'message': 'Project created successfully',
            'project_id': project.id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating project: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/projects/<int:project_id>', methods=['GET'])
@login_required
@require_organization_access()
def get_project(project_id):
    """Get a specific project"""
    try:
        project = Project.query.filter_by(
            id=project_id,
            organization_id=current_user.organization_id
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({
            'id': project.id,
            'client_name': project.client_name,
            'project_name': project.project_name,
            'language_pair': project.language_pair,
            'content_type': project.content_type,
            'start_date': project.start_date.isoformat() if project.start_date else None,
            'due_date': project.due_date.isoformat() if project.due_date else None,
            'initial_word_count': project.initial_word_count,
            'translated_words': project.translated_words,
            'status': project.status,
            'gpo_risk_status': project.gpo_risk_status,
            'gpo_risk_reason': project.gpo_risk_reason,
            'gpo_recommendation': project.gpo_recommendation,
            'assigned_linguist_id': project.assigned_linguist_id,
            'source_file_path': project.source_file_path,
            'created_by': project.created_by,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting project: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/projects/<int:project_id>', methods=['PUT'])
@login_required
@require_role(['admin', 'project_manager'])
@require_organization_access()
def update_project(project_id):
    """Update a project"""
    try:
        project = Project.query.filter_by(
            id=project_id,
            organization_id=current_user.organization_id
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'client_name' in data:
            project.client_name = data['client_name']
        if 'project_name' in data:
            project.project_name = data['project_name']
        if 'language_pair' in data:
            project.language_pair = data['language_pair']
        if 'content_type' in data:
            project.content_type = data['content_type']
        if 'start_date' in data:
            project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'due_date' in data:
            project.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        if 'status' in data:
            project.status = data['status']
        if 'gpo_risk_status' in data:
            project.gpo_risk_status = data['gpo_risk_status']
        if 'gpo_risk_reason' in data:
            project.gpo_risk_reason = data['gpo_risk_reason']
        if 'gpo_recommendation' in data:
            project.gpo_recommendation = data['gpo_recommendation']
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log activity
        log_user_activity('update', 'project', str(project.id), {
            'project_name': project.project_name,
            'updated_fields': list(data.keys())
        })
        
        return jsonify({'message': 'Project updated successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error updating project: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@login_required
@require_role(['admin'])
@require_organization_access()
def delete_project(project_id):
    """Delete a project"""
    try:
        project = Project.query.filter_by(
            id=project_id,
            organization_id=current_user.organization_id
        ).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        project_name = project.project_name
        db.session.delete(project)
        db.session.commit()
        
        # Log activity
        log_user_activity('delete', 'project', str(project_id), {
            'project_name': project_name
        })
        
        return jsonify({'message': 'Project deleted successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting project: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

# User Management API
@api_bp.route('/users', methods=['GET'])
@login_required
@require_role(['admin'])
@require_organization_access()
def get_users():
    """Get all users in the organization"""
    try:
        users = User.query.filter_by(organization_id=current_user.organization_id).all()
        
        return jsonify({
            'users': [{
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'status': user.status,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'login_count': user.login_count,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            } for user in users]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting users: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/users', methods=['POST'])
@login_required
@require_role(['admin'])
@require_organization_access()
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'name', 'role', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Check organization limits
        from middleware import check_organization_limits
        limits = check_organization_limits()
        if limits and limits.get('limit') == 'users':
            return jsonify({
                'error': f'User limit reached ({limits["current"]}/{limits["max"]})'
            }), 400
        
        # Create user
        from werkzeug.security import generate_password_hash
        user = User()
        user.id = str(uuid.uuid4())
        user.email = data['email']
        user.name = data['name']
        user.password_hash = generate_password_hash(data['password'])
        user.role = data['role']
        user.organization_id = current_user.organization_id
        user.status = 'active'
        
        db.session.add(user)
        db.session.commit()
        
        # Log activity
        log_user_activity('create', 'user', user.id, {
            'email': user.email,
            'name': user.name,
            'role': user.role
        })
        
        return jsonify({
            'message': 'User created successfully',
            'user_id': user.id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating user: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

# Analytics API
@api_bp.route('/analytics/dashboard', methods=['GET'])
@login_required
@require_organization_access()
def get_dashboard_analytics():
    """Get dashboard analytics"""
    try:
        # Get basic counts
        total_projects = Project.query.filter_by(organization_id=current_user.organization_id).count()
        active_projects = Project.query.filter_by(
            organization_id=current_user.organization_id,
            status='In Progress'
        ).count()
        completed_projects = Project.query.filter_by(
            organization_id=current_user.organization_id,
            status='Completed'
        ).count()
        total_users = User.query.filter_by(organization_id=current_user.organization_id).count()
        
        # Get risk distribution
        risk_stats = db.session.query(
            Project.gpo_risk_status,
            func.count(Project.id)
        ).filter_by(organization_id=current_user.organization_id).group_by(Project.gpo_risk_status).all()
        
        risk_distribution = {status: count for status, count in risk_stats}
        
        # Get recent activity
        recent_projects = Project.query.filter_by(
            organization_id=current_user.organization_id
        ).order_by(desc(Project.created_at)).limit(5).all()
        
        # Get word count statistics
        word_stats = db.session.query(
            func.sum(Project.initial_word_count).label('total_words'),
            func.sum(Project.translated_words).label('translated_words')
        ).filter_by(organization_id=current_user.organization_id).first()
        
        total_words = word_stats.total_words if word_stats and word_stats.total_words else 0
        translated_words = word_stats.translated_words if word_stats and word_stats.translated_words else 0
        progress_percentage = (translated_words / total_words * 100) if total_words > 0 else 0
        
        return jsonify({
            'overview': {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'completed_projects': completed_projects,
                'total_users': total_users
            },
            'risk_distribution': risk_distribution,
            'progress': {
                'total_words': total_words,
                'translated_words': translated_words,
                'progress_percentage': round(progress_percentage, 2)
            },
            'recent_projects': [{
                'id': p.id,
                'project_name': p.project_name,
                'status': p.status,
                'created_at': p.created_at.isoformat()
            } for p in recent_projects]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting analytics: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/analytics/projects', methods=['GET'])
@login_required
@require_organization_access()
def get_project_analytics():
    """Get project analytics"""
    try:
        # Get projects by status
        status_stats = db.session.query(
            Project.status,
            func.count(Project.id)
        ).filter_by(organization_id=current_user.organization_id).group_by(Project.status).all()
        
        # Get projects by month (last 12 months)
        monthly_stats = db.session.query(
            func.date_trunc('month', Project.created_at).label('month'),
            func.count(Project.id)
        ).filter(
            Project.organization_id == current_user.organization_id,
            Project.created_at >= datetime.utcnow() - timedelta(days=365)
        ).group_by(func.date_trunc('month', Project.created_at)).order_by('month').all()
        
        # Get top clients
        client_stats = db.session.query(
            Project.client_name,
            func.count(Project.id).label('project_count')
        ).filter_by(organization_id=current_user.organization_id).group_by(
            Project.client_name
        ).order_by(desc('project_count')).limit(10).all()
        
        return jsonify({
            'status_distribution': {status: count for status, count in status_stats},
            'monthly_trends': [{
                'month': month.strftime('%Y-%m'),
                'count': count
            } for month, count in monthly_stats],
            'top_clients': [{
                'client_name': client,
                'project_count': count
            } for client, count in client_stats]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting project analytics: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Notifications API
@api_bp.route('/notifications', methods=['GET'])
@login_required
@require_organization_access()
def get_notifications():
    """Get user notifications"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = Notification.query.filter_by(user_id=current_user.id)
        
        if unread_only:
            query = query.filter_by(read=False)
        
        notifications = query.order_by(desc(Notification.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'notifications': [{
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.notification_type,
                'read': n.read,
                'action_url': n.action_url,
                'created_at': n.created_at.isoformat()
            } for n in notifications.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': notifications.total,
                'pages': notifications.pages,
                'has_next': notifications.has_next,
                'has_prev': notifications.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting notifications: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
@require_organization_access()
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
        
        notification.read = True
        db.session.commit()
        
        return jsonify({'message': 'Notification marked as read'})
        
    except Exception as e:
        current_app.logger.error(f"Error marking notification read: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/notifications/read-all', methods=['POST'])
@login_required
@require_organization_access()
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        Notification.query.filter_by(
            user_id=current_user.id,
            read=False
        ).update({'read': True})
        
        db.session.commit()
        
        return jsonify({'message': 'All notifications marked as read'})
        
    except Exception as e:
        current_app.logger.error(f"Error marking all notifications read: {e}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500 