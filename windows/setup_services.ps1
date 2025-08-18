$ErrorActionPreference = 'Stop'

function Exe($p){ if (Test-Path $p){ return $p } else { throw "Файл не найден: $p" } }

# Пути
$proj = (Resolve-Path .).Path
$python = Join-Path $proj 'venv\Scripts\python.exe'
$nssm = "C:\\Program Files\\nssm\\win64\\nssm.exe"
if (-not (Test-Path $nssm)) { $nssm = "C:\\Program Files (x86)\\nssm\\win64\\nssm.exe" }

if (-not (Test-Path $nssm)) { Write-Host "NSSM не найден. Установите: choco install nssm -y" -ForegroundColor Yellow; exit 1 }

# Установка служб
& $nssm install SolanaTradingBotWeb $python "$proj\\run.py"
& $nssm set SolanaTradingBotWeb AppDirectory $proj
& $nssm start SolanaTradingBotWeb

& $nssm install SolanaTradingWorker $python "$proj\\run_worker.py"
& $nssm set SolanaTradingWorker AppDirectory $proj
& $nssm start SolanaTradingWorker

& $nssm install SolanaTradingSniper $python "$proj\\run_sniper.py"
& $nssm set SolanaTradingSniper AppDirectory $proj
& $nssm start SolanaTradingSniper

Write-Host "Службы установлены и запущены" -ForegroundColor Green