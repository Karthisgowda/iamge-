@echo off
cd /d "%~dp0"
echo ===============================================
echo Image Recognition App - Local Launcher
echo ===============================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Install Python and enable "Add Python to PATH".
    pause
    exit /b 1
)

if not exist app.py (
    echo Error: app.py was not found in this folder.
    echo Open the folder that contains app.py, then run this file again.
    pause
    exit /b 1
)

python -m pip install -r local-requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Package installation failed.
    pause
    exit /b 1
)

start http://localhost:5000
python app.py
pause
