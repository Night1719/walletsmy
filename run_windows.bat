@echo off
chcp 65001 >nul
echo ========================================
echo BG Survey Platform - Windows Launcher
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add to PATH" during installation
    pause
    exit /b 1
)

echo Python found. Checking version...
python --version

echo.
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Creating necessary directories...
if not exist logs mkdir logs
if not exist static\images mkdir static\images

echo.
echo Initializing database...
python init_db.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)

echo.
echo Creating admin user...
python create_admin.py
if errorlevel 1 (
    echo ERROR: Failed to create admin user
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Starting BG Survey Platform...
echo.
echo The application will be available at:
echo http://localhost:5000
echo.
echo Default users:
echo - Admin: admin / admin123
echo - Test: test_user / test123
echo - User: user / user123
echo.
echo Press Ctrl+C to stop the application
echo.

python app.py

pause