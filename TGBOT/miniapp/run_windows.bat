@echo off
echo Starting Telegram Mini App for Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Set environment variables
set TELEGRAM_BOT_TOKEN=your_bot_token_here
set FILE_SERVER_BASE_URL=https://files.example.com
set FILE_SERVER_USER=your_file_server_user
set FILE_SERVER_PASS=your_file_server_password
set MINIAPP_URL=http://localhost:4477/miniapp
set FLASK_SECRET_KEY=your_secret_key_here
set MINIAPP_HOST=0.0.0.0
set MINIAPP_PORT=4477
set MINIAPP_DEBUG=true

REM Start the application
echo Starting Mini App on http://localhost:4477...
echo.
echo Press Ctrl+C to stop the server
echo.
python run.py

pause