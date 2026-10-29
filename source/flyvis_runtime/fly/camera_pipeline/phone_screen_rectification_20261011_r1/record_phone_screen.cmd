@echo off
echo Prepare the existing phone player and keep the whole white square visible.
echo In the preview press R. Tap the phone only after the green RECORDING cue.
echo Q stops. Recording is bounded to 12 seconds; startup wait is preview only.
"%~dp0..\..\.venv\Scripts\python.exe" "%~dp0record_selfserve.py" --user-authorized --duration-s 12 --preview-timeout-s 180
pause
