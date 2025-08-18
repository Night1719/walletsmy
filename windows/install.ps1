Param(
    [switch]$NoServices
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg){ Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Ok($msg){ Write-Host "[ OK ] $msg" -ForegroundColor Green }
function Write-Warn($msg){ Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg){ Write-Host "[ERR ] $msg" -ForegroundColor Red }

# Admin check
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Err "Запустите PowerShell от имени администратора"
    exit 1
}

Write-Info "Инициализация установки для Windows..."

# Execution policy for this process
Set-ExecutionPolicy RemoteSigned -Scope Process -Force

# Check Chocolatey
function Ensure-Choco {
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Warn "Chocolatey не найден. Установить? (Y/N)"
        $answer = Read-Host
        if ($answer -match '^[Yy]') {
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
            Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
            RefreshEnv.cmd | Out-Null
            Write-Ok "Chocolatey установлен"
        } else {
            Write-Warn "Chocolatey не будет установлен"
        }
    } else {
        Write-Ok "Chocolatey найден"
    }
}

Ensure-Choco

# Optionally install Python, Git, NSSM via choco
function Ensure-Package($name){
    if (Get-Command $name -ErrorAction SilentlyContinue) { Write-Ok "$name найден"; return }
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Info "Установка $name через choco..."
        choco install $name -y | Out-Null
        Write-Ok "$name установлен"
    } else {
        Write-Warn "Установите $name вручную или запустите скрипт снова"
    }
}

Ensure-Package python
Ensure-Package git
Ensure-Package nssm

# Start Postgres & Redis via Docker
function Ensure-DockerService($service){
    $composeCmd = (Get-Command 'docker' -ErrorAction SilentlyContinue) ? 'docker compose' : 'docker-compose'
    Write-Info "Старт контейнера $service..."
    & cmd /c "$composeCmd up -d $service" | Out-Null
}

Ensure-DockerService postgres
Ensure-DockerService redis

# Python venv
if (-not (Test-Path ./venv)) {
    Write-Info "Создание виртуального окружения..."
    python -m venv venv
}
Write-Ok "venv готов"

# Activate venv
$venvActivate = Join-Path (Resolve-Path ./venv).Path 'Scripts/Activate.ps1'
. $venvActivate

# Upgrade pip and install deps
Write-Info "Установка Python-зависимостей..."
pip install --upgrade pip setuptools wheel | Out-Null
pip install -r requirements.txt | Out-Null
if (Test-Path requirements-dev.txt) { pip install -r requirements-dev.txt | Out-Null }
Write-Ok "Зависимости установлены"

# .env
if (-not (Test-Path ./.env)) {
    if (Test-Path ./.env.example) { Copy-Item ./.env.example ./.env }
    Write-Ok ".env создан"
}

# logs
New-Item -ItemType Directory -Force -Path ./logs | Out-Null

# Alembic migrations
Write-Info "Применение миграций Alembic..."
python -m alembic upgrade head
Write-Ok "Миграции применены"

# Start services (optional)
if (-not $NoServices) {
    Write-Info "Запуск компонентов в отдельных окнах..."
    ./windows/run_all.ps1
}

Write-Ok "Установка завершена. Проверьте ./windows/health_check.ps1"