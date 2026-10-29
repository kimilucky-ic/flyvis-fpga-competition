@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_flyvis_demo.ps1" -Stream -Desktop -StreamSeconds 20
if errorlevel 1 (
  echo FlyVis could not complete startup or shutdown. Keep the logs for inspection.
  pause
)
