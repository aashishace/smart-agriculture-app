#!/usr/bin/env python3
"""
Smart Agriculture App - Main Application Entry Point
Run this file to start the Flask development server.
"""

import os
from dotenv import load_dotenv
from app import create_app
from flask_migrate import upgrade

# Load environment variables from .env file
load_dotenv()

def deploy():
    """Run deployment tasks."""
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    
    with app.app_context():
        # Create database tables
        from flask_migrate import init, migrate, upgrade
        try:
            upgrade()
        except:
            # If no migrations exist, create initial migration
            init()
            migrate()
            upgrade()

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'development')
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )
