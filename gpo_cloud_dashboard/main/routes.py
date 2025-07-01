from flask import render_template, redirect, url_for, flash, request, g, current_app, abort
from flask_login import login_required, current_user
from . import main_bp
from ..models import db, Project, User


@main_bp.before_request
def set_tenant_context():
    """Set tenant context for multi-tenancy"""
    if current_user.is_authenticated:
        g.current_tenant_id = current_user.tenant_id


@main_bp.route('/')
def index():
    """Landing page route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', title='Welcome to GPO')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route"""
    # Get projects for current tenant
    projects = Project.query.filter_by(tenant_id=g.current_tenant_id).all()
    
    # Get project statistics
    draft_count = sum(1 for p in projects if p.status == 'Draft')
    pending_count = sum(1 for p in projects if p.status == 'Pending Analysis')
    completed_count = sum(1 for p in projects if p.status == 'Analysis Complete')
    
    return render_template(
        'dashboard/dashboard.html',
        title='Dashboard',
        projects=projects,
        draft_count=draft_count,
        pending_count=pending_count,
        completed_count=completed_count
    )


@main_bp.route('/new_project_request')
@login_required
def new_project_request():
    """Placeholder for new project request route"""
    flash('This feature will be implemented in a future update.', 'info')
    return redirect(url_for('main.dashboard'))


@main_bp.route('/linguists/upload')
@login_required
def upload_linguists():
    """Placeholder for linguist upload route"""
    flash('This feature will be implemented in a future update.', 'info')
    return redirect(url_for('main.dashboard'))


@main_bp.route('/settings')
@login_required
def settings():
    """Placeholder for settings route"""
    flash('This feature will be implemented in a future update.', 'info')
    return redirect(url_for('main.dashboard'))


@main_bp.app_errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('errors/500.html'), 500 