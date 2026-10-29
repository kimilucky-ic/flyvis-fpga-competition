@echo off
chcp 65001 >nul
cd /d "%~dp0"
title FlyVis - PURE FPGA CAMERA 60 SECONDS
echo 纯FPGA真实摄像头60秒：请先正常关闭其他占用8771的FlyVis实验台。
echo 不启动GPU。请手动打开 http://127.0.0.1:8771/#competition
echo 板端运行固定文件 FlyVis纯FPGA摄像头60秒.ipynb 的唯一代码格。
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_gui.ps1" -Line11DDR -Line11LiveCamera -Line11PCAddress 192.168.2.89
if errorlevel 1 pause
