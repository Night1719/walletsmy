$ErrorActionPreference = 'Stop'

# Определяем корень проекта и переходим в него
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $ProjectRoot

# Ищем Python
$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue) }
if (-not $py) { throw 'Python not found. Install Python 3.9+ and add to PATH.' }

# Готовим venv
$VenvPath = Join-Path $ProjectRoot 'venv'
$Activate = Join-Path $VenvPath 'Scripts/Activate.ps1'
if (-not (Test-Path $Activate)) {
    & $py.Source -m venv $VenvPath
}
. $Activate

# Установка зависимостей
python -m pip install --upgrade pip setuptools wheel | Out-Null
python -m pip install -r requirements.txt | Out-Null

Write-Host "[SNIPER] Запуск Sniper Bot" -ForegroundColor Green
python run_sniper.py