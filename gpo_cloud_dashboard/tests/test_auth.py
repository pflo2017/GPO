import pytest
from flask import url_for
from ..models import User, Tenant

def test_login_page(client):
    """Test that the login page loads correctly"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data

def test_register_page(client):
    """Test that the register page loads correctly"""
    response = client.get('/auth/register')
    # Should redirect to create tenant if no tenants exist
    assert response.status_code == 302
    assert '/auth/create-tenant' in response.location

def test_create_tenant_page(client):
    """Test that the create tenant page loads correctly"""
    response = client.get('/auth/create-tenant')
    assert response.status_code == 200
    assert b'Welcome to GPO' in response.data

def test_user_registration(client, app):
    """Test user registration process"""
    # First create a tenant
    with app.app_context():
        tenant = Tenant(name='Test Tenant')
        app.db.session.add(tenant)
        app.db.session.commit()
        tenant_id = tenant.id
    
    # Now register a user
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'tenant_id': tenant_id,
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful' in response.data
    
    # Check that the user was created
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'test@example.com'
        assert user.tenant_id == tenant_id
        assert user.role == 'PM'

def test_login_logout(client, app):
    """Test login and logout functionality"""
    # First create a tenant and user
    with app.app_context():
        tenant = Tenant(name='Test Tenant')
        app.db.session.add(tenant)
        app.db.session.flush()
        
        user = User(
            username='testuser',
            email='test@example.com',
            tenant_id=tenant.id,
            role='PM'
        )
        user.set_password('password123')
        app.db.session.add(user)
        app.db.session.commit()
    
    # Test login
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'password123',
        'remember_me': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Welcome back' in response.data
    
    # Test logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data 