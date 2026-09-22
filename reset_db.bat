@echo off
chcp 65001 >nul
title Bienestar Estudiantil - Reset Base de Datos
echo ============================================
echo   RESET BASE DE DATOS
echo ============================================
echo.
echo Esto eliminara TODOS los datos y recargara
echo los datos de prueba iniciales.
echo.
set /p confirm="¿Continuar? (S/N): "
if /i not "%confirm%"=="S" (
    echo Operacion cancelada.
    pause
    exit /b
)

echo.
echo [1/3] Deteniendo servidor...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Eliminando base de datos anterior...
"%~dp0backend\venv\Scripts\python.exe" -c "import psycopg2; from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT; conn=psycopg2.connect(dbname='postgres',user='postgres',password='sena2024',host='127.0.0.1',port='5432'); conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT); cur=conn.cursor(); cur.execute(\"DROP DATABASE IF EXISTS bienestar_estudiantil\"); print('Base de datos eliminada.'); cur.close(); conn.close()"

echo [3/3] Recreando base de datos y datos...
"%~dp0backend\venv\Scripts\python.exe" "%~dp0create_db.py"
cd /d "%~dp0backend"
"%~dp0backend\venv\Scripts\python.exe" seed.py
cd /d "%~dp0"

echo.
echo ============================================
echo   BASE DE DATOS REINICIADA
echo ============================================
echo.
pause
