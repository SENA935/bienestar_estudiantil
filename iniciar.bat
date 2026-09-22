@echo off
chcp 65001 >nul
title Bienestar Estudiantil - Servidor
echo ============================================
echo   BIENESTAR ESTUDIANTIL
echo   Iniciando servidor...
echo ============================================
echo.
echo   URL: http://localhost:5000
echo.
echo   Credenciales:
echo     Admin:       admin / admin123
echo     Coordinador: coordinador / coord123
echo     Docente:     docente1 / doc123
echo     Estudiante:  est1 / est123
echo.
echo   Presione CTRL+C para detener el servidor.
echo ============================================
echo.

cd /d "%~dp0backend"
"%~dp0backend\venv\Scripts\python.exe" run.py
pause
