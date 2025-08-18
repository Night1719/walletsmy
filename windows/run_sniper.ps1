$ErrorActionPreference = 'Stop'
if (-not (Test-Path ./venv)) { python -m venv venv }
. ./venv/Scripts/Activate.ps1
pip install -r requirements.txt | Out-Null
Write-Host "[SNIPER] Запуск Sniper Bot" -ForegroundColor Green
python run_sniper.py