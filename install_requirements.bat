@echo off
echo.
echo ========================================================
echo  Smart Crop Care Assistant - Python Dependency Installer 
echo ========================================================
echo.
echo This script will install all the Python packages required to run the application.
echo.
echo IMPORTANT: Please make sure you have created and activated a Python
echo virtual environment before running this script.
echo.
echo See CONTRIBUTING_GUIDE.md for full setup instructions.
echo.
pause
echo.
echo Installing packages from requirements.txt...
echo.

pip install -r requirements.txt

echo.
echo ========================================================
echo                  Installation Complete!
echo ========================================================
echo.
echo All Python packages have been installed.
echo You can now proceed with setting up the database as described in the guide.
echo.
pause
