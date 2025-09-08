# Telegram Mini App Launcher for Windows
# PowerShell script for running the Mini App

Write-Host "🚀 Starting Telegram Mini App for Windows..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Set environment variables
Write-Host "⚙️ Setting environment variables..." -ForegroundColor Yellow
$env:TELEGRAM_BOT_TOKEN = "your_bot_token_here"
$env:FILE_SERVER_BASE_URL = "https://files.example.com"
$env:FILE_SERVER_USER = "your_file_server_user"
$env:FILE_SERVER_PASS = "your_file_server_password"
$env:MINIAPP_URL = "http://localhost:5000/miniapp"
$env:FLASK_SECRET_KEY = "your_secret_key_here"
$env:MINIAPP_HOST = "0.0.0.0"
$env:MINIAPP_PORT = "5000"
$env:MINIAPP_DEBUG = "true"

# Start the application
Write-Host ""
Write-Host "🌐 Starting Mini App on http://localhost:5000..." -ForegroundColor Green
Write-Host "📱 Mini App URL: http://localhost:5000/miniapp" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python run.py