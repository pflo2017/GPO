from flask import render_template, redirect, url_for, flash, request, g, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from . import auth_bp
from ..models import db, User, Tenant
from .forms import LoginForm, RegistrationForm, CreateTenantForm

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Find user by username
        user = User.query.filter_by(username=form.username.data).first()
        
        # Check if user exists and password is correct
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        # Log in user
        login_user(user, remember=form.remember_me.data)
        
        # Set current tenant in g
        g.current_tenant_id = user.tenant_id
        
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Check if any tenants exist
    tenant_exists = Tenant.query.first() is not None
    
    # If no tenants exist, redirect to create first tenant
    if not tenant_exists:
        return redirect(url_for('auth.create_tenant'))
    
    form = RegistrationForm()
    
    # Populate tenant choices
    form.tenant_id.choices = [(t.id, t.name) for t in Tenant.query.all()]
    
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            tenant_id=form.tenant_id.data,
            role='PM'  # Default role is PM
        )
        user.set_password(form.password.data)
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/create-tenant', methods=['GET', 'POST'])
def create_tenant():
    """Create first tenant and admin user"""
    # Check if any tenants exist
    tenant_exists = Tenant.query.first() is not None
    
    # If tenants exist and user is not authenticated, redirect to register
    if tenant_exists and not current_user.is_authenticated:
        return redirect(url_for('auth.register'))
    
    # If tenants exist and user is not admin, redirect to dashboard
    if tenant_exists and not current_user.is_admin:
        flash('You do not have permission to create tenants.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = CreateTenantForm()
    if form.validate_on_submit():
        # Create new tenant
        tenant = Tenant(name=form.tenant_name.data)
        db.session.add(tenant)
        db.session.flush()  # Flush to get tenant ID
        
        # Create admin user if this is the first tenant
        if not tenant_exists:
            admin_user = User(
                username=form.admin_username.data,
                email=form.admin_email.data,
                tenant_id=tenant.id,
                role='Admin'
            )
            admin_user.set_password(form.admin_password.data)
            db.session.add(admin_user)
        
        db.session.commit()
        
        if not tenant_exists:
            flash('Tenant and admin user created successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(f'Tenant "{tenant.name}" created successfully!', 'success')
            return redirect(url_for('main.dashboard'))
    
    return render_template(
        'auth/create_tenant.html', 
        title='Create Tenant', 
        form=form, 
        first_tenant=not tenant_exists
    ) 