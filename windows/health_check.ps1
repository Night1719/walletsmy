$ErrorActionPreference = 'SilentlyContinue'

function Test-Http($url){
    try { $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 -Uri $url; return $r.StatusCode -eq 200 } catch { return $false }
}

Write-Host "=== Health Check (Windows) ===" -ForegroundColor Cyan

# Processes
$web = (Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*python*' -and $_.MainWindowTitle -like '*run.py*' })
$worker = (Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*python*' -and $_.MainWindowTitle -like '*run_worker.py*' })
$sniper = (Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*python*' -and $_.MainWindowTitle -like '*run_sniper.py*' })

Write-Host ("WEB:     " + ($(if($web){'OK'}else{'DOWN'})))
Write-Host ("WORKER:  " + ($(if($worker){'OK'}else{'DOWN'})))
Write-Host ("SNIPER:  " + ($(if($sniper){'OK'}else{'DOWN'})))

# Ports
$ports = @(
    @{name='FastAPI'; port=8000},
    @{name='Postgres'; port=5432},
    @{name='Redis'; port=6379}
)
foreach($p in $ports){
    $res = Test-NetConnection -ComputerName 'localhost' -Port $p.port -WarningAction SilentlyContinue
    Write-Host ("PORT {0,-8}: {1}" -f $p.name, $(if($res.TcpTestSucceeded){'OPEN'}else{'CLOSED'}))
}

# HTTP
Write-Host ("/api/health:   " + ($(if(Test-Http 'http://localhost:8000/api/health'){'OK'}else{'FAIL'})))
Write-Host ("/api/metrics:  " + ($(if(Test-Http 'http://localhost:8000/api/metrics'){'OK'}else{'FAIL'})))