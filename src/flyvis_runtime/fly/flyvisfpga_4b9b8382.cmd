@echo off
chcp 65001 >nul
cd /d "%~dp0"
title FlyVis - PURE FPGA ON60 485 steps
echo 纯FPGA ON60：请先正常关闭占用8771的GPU联合实验台。
echo 本入口不启动GPU或摄像头。启动后手动打开 http://127.0.0.1:8771/#competition
echo 板端运行固定文件 FlyVis纯FPGA_ON60实验.ipynb 的唯一代码格。
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_gui.ps1" -Line11DDR -Line11Steps 485 -Line11PCAddress 192.168.2.89
if errorlevel 1 pause
