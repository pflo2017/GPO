import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration - Supabase PostgreSQL
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_HOST = os.environ.get('SUPABASE_HOST')
    SUPABASE_PORT = os.environ.get('SUPABASE_PORT')
    SUPABASE_DB = os.environ.get('SUPABASE_DB')
    SUPABASE_USER = os.environ.get('SUPABASE_USER')
    SUPABASE_PASSWORD = os.environ.get('SUPABASE_PASSWORD')
    
    # Construct database URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # API key for Local Brain authentication
    LOCAL_BRAIN_API_KEY = os.environ.get('LOCAL_BRAIN_API_KEY')
    
    # AI Configuration
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    
    # Application name
    APP_NAME = "GPO Central Intelligence Dashboard"


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # In production, ensure SECRET_KEY is set in environment
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Set secure cookie
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 