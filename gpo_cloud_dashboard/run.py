import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # Use production config from environment variable or default to development
    flask_env = os.getenv('FLASK_ENV', 'development')
    config_name = 'production' if flask_env == 'production' else 'development'
    
    print(f"Starting GPO Central Intelligence Dashboard in {config_name} mode...")
    
    # Create app with the appropriate configuration
    app = create_app(config_name)
    
    # Run the app
    port = int(os.getenv('PORT', 5000))
    debug = config_name != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug) 