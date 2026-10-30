@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_flyvis_demo.ps1" -Skeleton -Camera -Desktop -StreamSeconds 60
if errorlevel 1 (
  echo FlyVis could not complete startup or shutdown. Keep this window and the session logs.
  pause
)
