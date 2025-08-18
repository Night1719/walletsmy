$ErrorActionPreference = 'Stop'
$nssm = "C:\\Program Files\\nssm\\win64\\nssm.exe"
if (-not (Test-Path $nssm)) { $nssm = "C:\\Program Files (x86)\\nssm\\win64\\nssm.exe" }
if (-not (Test-Path $nssm)) { Write-Host "NSSM не найден" -ForegroundColor Yellow; exit 0 }

$names = @('SolanaTradingBotWeb','SolanaTradingWorker','SolanaTradingSniper')
foreach($n in $names){
    & $nssm stop $n 2>$null
    & $nssm remove $n confirm 2>$null
}
Write-Host "Службы NSSM удалены" -ForegroundColor Green