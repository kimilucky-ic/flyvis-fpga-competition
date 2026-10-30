@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch.ps1" -Action setup -Device cuda %*
set "TEAM_EXIT=%ERRORLEVEL%"
echo.
echo Logs: "%~dp0logs"
pause
exit /b %TEAM_EXIT%
