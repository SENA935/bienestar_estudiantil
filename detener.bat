@echo off
chcp 65001 >nul
echo ============================================
echo   Deteniendo servidor...
echo ============================================
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Bienestar*" >nul 2>&1
taskkill /F /IM python.exe /FI "IMAGENAME eq python.exe" >nul 2>&1
echo   Servidor detenido.
echo.
pause
