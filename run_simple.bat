@echo off
echo BG Survey Platform - Simple Launcher
echo ====================================
echo.

echo Checking Python...
python --version
if errorlevel 1 (
    echo Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Initializing database...
python init_db.py

echo.
echo Creating admin user...
python create_admin.py

echo.
echo Starting application...
echo.
echo Open browser: http://localhost:5000
echo Users: admin/admin123, test_user/test123, user/user123
echo.
echo Press Ctrl+C to stop
echo.

python app.py

pause