@echo off
echo ========================================
echo LinkedIn Event Photo Curator
echo Quick Start Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
    echo Virtual environment created!
) else (
    echo [2/4] Virtual environment already exists
)
echo.

REM Activate virtual environment and install dependencies
echo [3/4] Installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo.

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Copying from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file with your LinkedIn API credentials
    echo Visit: https://www.linkedin.com/developers/apps
    echo.
    pause
)

echo [4/4] Starting application...
echo.
echo ========================================
echo Application will start at:
echo http://localhost:8000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

pause
