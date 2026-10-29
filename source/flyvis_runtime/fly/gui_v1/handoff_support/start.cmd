@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 backend\frozen_server.py
goto finished
:usepython
python backend\frozen_server.py
:finished
if errorlevel 1 pause
endlocal
