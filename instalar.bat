@echo off
chcp 65001 >nul
title Bienestar Estudiantil - Instalación
echo ============================================
echo   BIENESTAR ESTUDIANTIL - INSTALACIÓN
echo ============================================
echo.

echo [1/6] Verificando Python...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado. Instale Python 3.12+
    pause
    exit /b 1
)
py --version
echo OK
echo.

echo [2/6] Creando entorno virtual...
if exist "%~dp0backend\venv" (
    echo Ya existe el entorno virtual.
) else (
    py -m venv "%~dp0backend\venv"
    echo Entorno virtual creado.
)
echo.

echo [3/6] Instalando dependencias...
"%~dp0backend\venv\Scripts\pip.exe" install -r "%~dp0backend\requirements.txt" --quiet
echo Dependencias instaladas.
echo.

echo [4/6] Verificando PostgreSQL...
sc query postgresql-x64-16 | findstr "RUNNING" >nul 2>&1
if %errorlevel% neq 0 (
    echo PostgreSQL no esta corriendo. Intentando iniciar...
    net start postgresql-x64-16 >nul 2>&1
    if %errorlevel% neq 0 (
        echo ADVERTENCIA: No se pudo iniciar PostgreSQL automaticamente.
        echo Inicie PostgreSQL manualmente desde el Servicio de Windows.
    ) else (
        echo PostgreSQL iniciado correctamente.
    )
) else (
    echo PostgreSQL esta corriendo.
)
echo.

echo [5/6] Creando base de datos...
"%~dp0backend\venv\Scripts\python.exe" "%~dp0create_db.py"
echo.

echo [6/6] Cargando datos iniciales...
cd /d "%~dp0backend"
"%~dp0backend\venv\Scripts\python.exe" seed.py
cd /d "%~dp0"
echo.

echo ============================================
echo   INSTALACION COMPLETADA
echo ============================================
echo.
echo   Ejecute iniciar.bat para arrancar el servidor.
echo.
pause
