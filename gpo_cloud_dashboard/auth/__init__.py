from flask import Blueprint

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Import routes
from . import routes 