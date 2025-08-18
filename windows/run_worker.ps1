$ErrorActionPreference = 'Stop'
if (-not (Test-Path ./venv)) { python -m venv venv }
. ./venv/Scripts/Activate.ps1
pip install -r requirements.txt | Out-Null
Write-Host "[WORKER] Запуск Celery worker" -ForegroundColor Green
python run_worker.py