"""
GPO Product Package
This file makes the gpo_product directory a Python package.
It also provides convenient imports for the main application components.
"""

import os
import sys

# Make sure the package directory is in the path
package_dir = os.path.dirname(os.path.abspath(__file__))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

# Import key components for easy access
try:
    from .app import app
    from .database import db, init_database
    from .auth import init_auth
    from .admin import init_admin
    from .api import api_bp
    
    __all__ = ['app', 'db', 'init_database', 'init_auth', 'init_admin', 'api_bp']
    
except ImportError:
    # Don't fail on import - this allows the package to be imported
    # even if some components aren't available yet
    pass

# Package metadata
__version__ = '1.0.0'
__author__ = 'GPO Team' 