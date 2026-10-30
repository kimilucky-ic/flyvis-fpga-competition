@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell.exe -WindowStyle Hidden -WorkingDirectory '%~dp0' -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','\"%~dp0start_gui.ps1\"','-OperatorSelect'"
