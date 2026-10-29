@echo off
setlocal
cd /d "%~dp0"
python -X utf8 -B run.py %*
if errorlevel 1 pause
