$ErrorActionPreference = 'Stop'
if (-not (Test-Path ./venv)) { python -m venv venv }
. ./venv/Scripts/Activate.ps1
pip install -r requirements.txt | Out-Null
Write-Host "[WEB] Запуск FastAPI на http://localhost:8000" -ForegroundColor Green
python run.py