@echo off
chcp 65001 >nul
echo ========================================
echo    BG Survey System - Windows Launch
echo ========================================
echo.

REM Check Python
echo [1/8] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Install Python from https://python.org
    pause
    exit /b 1
)
echo OK: Python found

REM Check manage.py
echo [2/8] Checking Django project...
if not exist "manage.py" (
    echo ERROR: manage.py not found!
    echo Make sure you are in the project folder
    echo.
    echo Current folder:
    cd
    echo.
    echo Folder contents:
    dir
    pause
    exit /b 1
)
echo OK: manage.py found

REM Create virtual environment
echo [3/8] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo OK: Virtual environment created
) else (
    echo OK: Virtual environment already exists
)

REM Activate virtual environment
echo [4/8] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo OK: Virtual environment activated

REM Upgrade pip
echo [5/8] Upgrading pip...
python -m pip install --upgrade pip
echo OK: pip upgraded

REM Install dependencies
echo [6/8] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo OK: Dependencies installed

REM Create directories
echo [7/8] Creating directories...
if not exist "staticfiles" mkdir staticfiles
if not exist "media" mkdir media
echo OK: Directories created

REM Create migrations
echo [8/8] Creating migrations...
python manage.py makemigrations users
python manage.py makemigrations surveys
echo OK: Migrations created

REM Apply migrations
echo.
echo ========================================
echo    Applying migrations...
echo ========================================
python manage.py migrate
echo OK: Migrations applied

REM Create superuser
echo.
echo ========================================
echo    Creating administrator...
echo ========================================
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None; user = User.objects.get(username='admin'); user.role = 'admin'; user.can_create_surveys = True; user.save()"
echo OK: Administrator created

REM Collect static files
echo.
echo ========================================
echo    Collecting static files...
echo ========================================
python manage.py collectstatic --noinput
echo OK: Static files collected

REM Start server
echo.
echo ========================================
echo    Starting development server...
echo ========================================
echo.
echo OK: Server started!
echo OK: Open browser and go to:
echo OK: http://127.0.0.1:8000
echo.
echo OK: Admin panel:
echo OK: http://127.0.0.1:8000/admin
echo OK: Login: admin
echo OK: Password: admin123
echo.
echo Press Ctrl+C to stop server
echo.

python manage.py runserver 127.0.0.1:8000

pause