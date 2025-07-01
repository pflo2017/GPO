#!/usr/bin/env python3
"""
GPO (Global Project Orchestrator) Runner

This script provides a unified interface to run either the GPO Cloud Dashboard or the GPO Local Brain.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Define the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

def setup_environment():
    """Set up the environment for the application"""
    # Load environment variables from .env file
    env_file = PROJECT_ROOT / '.env'
    if env_file.exists():
        print(f"Loading environment variables from {env_file}")
        load_dotenv(env_file)
    else:
        print("Warning: No .env file found. Using system environment variables.")

def run_cloud_dashboard():
    """Run the GPO Cloud Dashboard"""
    print("Starting GPO Cloud Dashboard...")
    
    # Add the cloud dashboard directory to the Python path
    cloud_dir = PROJECT_ROOT / 'gpo_cloud_dashboard'
    sys.path.insert(0, str(cloud_dir))
    
    # Set Flask environment variables
    os.environ['FLASK_APP'] = 'app.py'
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    # Import and run the application
    try:
        from gpo_cloud_dashboard.app import create_app
        
        # Use production config from environment variable or default to development
        flask_env = os.getenv('FLASK_ENV', 'development')
        config_name = 'production' if flask_env == 'production' else 'development'
        
        app = create_app(config_name)
        
        # Run the app
        port = int(os.getenv('PORT', 5000))
        debug = config_name != 'production'
        app.run(host='0.0.0.0', port=port, debug=debug)
    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure the GPO Cloud Dashboard is properly installed.")
        sys.exit(1)

def run_local_brain():
    """Run the GPO Local Brain"""
    print("Starting GPO Local Brain...")
    
    # Add the local brain directory to the Python path
    local_dir = PROJECT_ROOT / 'gpo_product'
    sys.path.insert(0, str(local_dir))
    
    # Set Flask environment variables
    os.environ['FLASK_APP'] = 'app.py'
    
    # Import and run the application
    try:
        sys.path.append(str(local_dir))
        from gpo_product.app import app
        
        # Run the app
        port = int(os.getenv('PORT', 5001))
        app.run(host='0.0.0.0', port=port, debug=True)
    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure the GPO Local Brain is properly installed.")
        sys.exit(1)

def main():
    """Main function to parse arguments and run the appropriate component"""
    parser = argparse.ArgumentParser(description='Run GPO components')
    parser.add_argument('component', choices=['cloud', 'local', 'both'], 
                        help='Which component to run: cloud (dashboard), local (brain), or both')
    parser.add_argument('--port-cloud', type=int, default=5000,
                        help='Port for the cloud dashboard (default: 5000)')
    parser.add_argument('--port-local', type=int, default=5001,
                        help='Port for the local brain (default: 5001)')
    
    args = parser.parse_args()
    
    # Set up environment
    setup_environment()
    
    # Set ports from arguments
    os.environ['PORT'] = str(args.port_cloud)
    
    # Run the selected component(s)
    if args.component == 'cloud':
        run_cloud_dashboard()
    elif args.component == 'local':
        os.environ['PORT'] = str(args.port_local)
        run_local_brain()
    elif args.component == 'both':
        # This is a simple implementation that runs the cloud component
        # For a production setup, you would use multiprocessing or separate processes
        print("Warning: Running both components in sequence, not in parallel.")
        print("For production, run them in separate terminals.")
        
        try:
            run_cloud_dashboard()
        except KeyboardInterrupt:
            pass
        
        os.environ['PORT'] = str(args.port_local)
        run_local_brain()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # If no arguments provided, show help
        sys.argv.append('--help')
    main()
