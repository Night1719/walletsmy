# BG Survey Platform - PowerShell Launcher
# =========================================

Write-Host "BG Survey Platform - PowerShell Launcher" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Virtual environment created successfully" -ForegroundColor Green
}

Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" }
if (!(Test-Path "static\images")) { New-Item -ItemType Directory -Path "static\images" -Force }

Write-Host ""

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Yellow
python init_db.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to initialize database" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Create admin user
Write-Host "Creating admin user..." -ForegroundColor Yellow
python create_admin.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create admin user" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Starting BG Survey Platform..." -ForegroundColor Yellow
Write-Host ""
Write-Host "The application will be available at:" -ForegroundColor Cyan
Write-Host "http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "Default users:" -ForegroundColor Cyan
Write-Host "- Admin: admin / admin123" -ForegroundColor White
Write-Host "- Test: test_user / test123" -ForegroundColor White
Write-Host "- User: user / user123" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

# Start the application
python app.py

Write-Host ""
Read-Host "Press Enter to exit"