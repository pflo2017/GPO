from flask import Blueprint

# Create blueprint
main_bp = Blueprint('main', __name__)

# Import routes
from . import routes 