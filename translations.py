#!/usr/bin/env python3
"""
Translation Management Script for Smart Crop Care Assistant
"""

import os
import sys
from flask import Flask
from flask_babel import Babel
from babel.messages import frontend as babel_frontend

def init_babel():
    """Initialize Flask-Babel for the application."""
    app = Flask(__name__)
    app.config['BABEL_DEFAULT_LOCALE'] = 'hi'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'Asia/Kolkata'
    app.config['LANGUAGES'] = {
        'en': 'English',
        'hi': 'हिंदी'
    }
    babel = Babel(app)
    return app, babel

def extract_messages():
    """Extract all translatable strings from the application."""
    print("🔍 Extracting messages from Python and template files...")
    
    # Extract command
    os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .')
    print("✅ Messages extracted to messages.pot")

def init_languages():
    """Initialize translation files for supported languages."""
    languages = ['en', 'hi']
    
    for lang in languages:
        print(f"🌐 Initializing {lang} translation...")
        if not os.path.exists(f'app/translations/{lang}'):
            os.system(f'pybabel init -i messages.pot -d app/translations -l {lang}')
            print(f"✅ Created translation files for {lang}")
        else:
            print(f"⏭️  Translation files for {lang} already exist")

def update_translations():
    """Update existing translation files with new messages."""
    print("🔄 Updating existing translations...")
    os.system('pybabel update -i messages.pot -d app/translations')
    print("✅ Translations updated")

def compile_translations():
    """Compile translation files for production use."""
    print("⚙️  Compiling translations...")
    os.system('pybabel compile -d app/translations')
    print("✅ Translations compiled")

def main():
    """Main function to handle translation operations."""
    if len(sys.argv) < 2:
        print("Usage: python translations.py [extract|init|update|compile|all]")
        return
    
    command = sys.argv[1]
    
    # Ensure we're in the right directory
    if not os.path.exists('babel.cfg'):
        print("❌ babel.cfg not found. Please run from the project root directory.")
        return
    
    # Create translations directory if it doesn't exist
    os.makedirs('app/translations', exist_ok=True)
    
    if command == 'extract':
        extract_messages()
    elif command == 'init':
        extract_messages()
        init_languages()
    elif command == 'update':
        extract_messages()
        update_translations()
    elif command == 'compile':
        compile_translations()
    elif command == 'all':
        extract_messages()
        init_languages()
        update_translations()
        compile_translations()
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: extract, init, update, compile, all")

if __name__ == '__main__':
    main()
