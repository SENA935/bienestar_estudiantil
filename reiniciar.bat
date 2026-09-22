@echo off
chcp 65001 >nul
title Bienestar Estudiantil - Reiniciar
echo ============================================
echo   Reiniciando servidor...
echo ============================================
echo.

echo [1/2] Deteniendo servidor actual...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo Servidor detenido.

echo.
echo [2/2] Iniciando servidor...
echo.
cd /d "%~dp0backend"
"%~dp0backend\venv\Scripts\python.exe" run.py
pause
