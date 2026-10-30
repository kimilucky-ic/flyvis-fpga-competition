@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch.ps1" -Action cpu_edge_golden -Device cpu %*
set "TEAM_EXIT=%ERRORLEVEL%"
pause
exit /b %TEAM_EXIT%
