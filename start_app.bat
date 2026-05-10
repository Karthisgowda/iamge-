@echo off
echo ===============================================
echo Image Recognition App - XAMPP Launcher
echo ===============================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo and make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM Make sure the uploads directory exists
if not exist uploads mkdir uploads
if not exist static\uploads mkdir static\\uploads

REM Run the application
echo Starting the application...
echo.
echo If the application doesn't start, please check:
echo 1. Make sure XAMPP is running with MySQL started
echo 2. Make sure you have all required packages installed
echo   (python -m pip install -r local-requirements.txt)
echo.
echo Press Ctrl+C to stop the application
echo.
echo Launching in your browser: http://localhost:5000
echo ===============================================
echo.

REM Open browser
start http://localhost:5000

REM Start the application
python run_xampp.py

paus