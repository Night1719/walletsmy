$proj = (Resolve-Path .).Path
$ps = (Get-Command powershell).Source

Start-Process $ps -ArgumentList "-NoExit -Command Set-Location '$proj'; ./windows/run_web.ps1"
Start-Process $ps -ArgumentList "-NoExit -Command Set-Location '$proj'; ./windows/run_worker.ps1"
Start-Process $ps -ArgumentList "-NoExit -Command Set-Location '$proj'; ./windows/run_sniper.ps1"