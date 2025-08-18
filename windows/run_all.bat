@echo off
setlocal
pushd %~dp0\..
start powershell -NoExit -Command ./windows/run_web.ps1
start powershell -NoExit -Command ./windows/run_worker.ps1
start powershell -NoExit -Command ./windows/run_sniper.ps1
popd
endlocal