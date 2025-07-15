#!/usr/bin/env python3
"""
Smart Crop Care Assistant Setup Script
Run this script to set up the development environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not supported")
        print("Please install Python 3.8 or higher")
        return False

def setup_virtual_environment():
    """Create and activate virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📁 Virtual environment already exists")
        return True
    
    print("📁 Creating virtual environment...")
    
    # Create virtual environment
    if not run_command("python -m venv venv", "Creating virtual environment"):
        return False
    
    print("✅ Virtual environment created successfully")
    return True

def install_dependencies():
    """Install Python dependencies."""
    
    # Get the appropriate python and pip commands based on OS
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python.exe"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Linux/Mac
        python_cmd = "venv/bin/python"
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip first using python -m pip (more reliable on Windows)
    if not run_command(f"{python_cmd} -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Pip upgrade failed, but continuing with installation...")
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True

def setup_environment_file():
    """Create .env file from example."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("📄 .env file already exists")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("📄 Created .env file from example")
        print("⚠️  Please edit .env file and add your API keys:")
        print("   - OPENWEATHER_API_KEY (get from openweathermap.org)")
        print("   - TWILIO credentials (optional, for SMS)")
        return True
    else:
        print("❌ .env.example file not found")
        return False

def create_upload_directory():
    """Create upload directory for images."""
    upload_dir = Path("app/static/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    print("📁 Created upload directory")
    return True

def initialize_database():
    """Initialize the database."""
    print("🗄️ Initializing database...")
    
    # Get the appropriate python command
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python.exe"
    else:  # Linux/Mac
        python_cmd = "venv/bin/python"
    
    # Create database tables
    init_script = """
from app import create_app, db
app = create_app('development')
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"""
    
    with open("init_db.py", "w") as f:
        f.write(init_script)
    
    success = run_command(f"{python_cmd} init_db.py", "Creating database tables")
    
    # Clean up
    if Path("init_db.py").exists():
        Path("init_db.py").unlink()
    
    return success

def main():
    """Main setup function."""
    print("🌾 Smart Crop Care Assistant Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to setup virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup environment file
    if not setup_environment_file():
        print("❌ Failed to setup environment file")
        sys.exit(1)
    
    # Create upload directory
    if not create_upload_directory():
        print("❌ Failed to create upload directory")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Activate virtual environment:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Linux/Mac
        print("   source venv/bin/activate")
    
    print("3. Run the application:")
    print("   python run.py")
    print("\n🌐 The app will be available at: http://localhost:5000")
    print("\n📚 Read README.md for more information")

if __name__ == "__main__":
    main()
