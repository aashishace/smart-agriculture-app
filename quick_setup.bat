@echo off
echo 🌾 Smart Agriculture App - Quick Setup for Windows
echo ================================================

echo.
echo 📁 Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip

echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt

echo.
echo 📄 Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file from example
) else (
    echo ✅ .env file already exists
)

echo.
echo 📁 Creating upload directory...
if not exist "app\static\uploads" mkdir "app\static\uploads"

echo.
echo 🗄️ Initializing database...
python -c "from app import create_app, db; app = create_app('development'); app.app_context().push(); db.create_all(); print('✅ Database initialized!')"

echo.
echo ================================================
echo 🎉 Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Edit .env file if needed (API keys already added)
echo 2. Run the application: python run.py
echo 3. Open browser: http://localhost:5000
echo.
echo Press any key to exit...
pause > nul
