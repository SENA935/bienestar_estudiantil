@echo off
chcp 65001 >nul
title Bienestar Estudiantil - Menú Principal
:menu
cls
echo ============================================
echo   BIENESTAR ESTUDIANTIL - MENÚ PRINCIPAL
echo ============================================
echo.
echo   [1] Instalar / Reinstalar
echo   [2] Iniciar servidor
echo   [3] Abrir en navegador
echo   [4] Detener servidor
echo   [5] Reiniciar servidor
echo   [6] Reset base de datos
echo   [7] Verificar estado
echo   [0] Salir
echo.
echo ============================================
echo.
set /p opcion="Seleccione una opción: "

if "%opcion%"=="1" goto instalar
if "%opcion%"=="2" goto iniciar
if "%opcion%"=="3" goto navegador
if "%opcion%"=="4" goto detener
if "%opcion%"=="5" goto reiniciar
if "%opcion%"=="6" goto reset
if "%opcion%"=="7" goto estado
if "%opcion%"=="0" goto salir
echo Opción no válida.
timeout /t 2 >nul
goto menu

:instalar
call "%~dp0instalar.bat"
goto menu

:iniciar
start "Bienestar Estudiantil" cmd /c "title Bienestar Estudiantil - Servidor && cd /d \"%~dp0backend\" && \"%~dp0backend\venv\Scripts\python.exe\" run.py"
timeout /t 3 >nul
echo Servidor iniciado en http://localhost:5000
timeout /t 2 >nul
goto menu

:navegador
start http://localhost:5000/login
goto menu

:detener
call "%~dp0detener.bat"
goto menu

:reiniciar
call "%~dp0reiniciar.bat"
goto menu

:reset
call "%~dp0reset_db.bat"
goto menu

:estado
cls
echo ============================================
echo   ESTADO DEL SISTEMA
echo ============================================
echo.
echo Python:
py --version 2>nul || echo   No encontrado
echo.
echo PostgreSQL:
sc query postgresql-x64-16 2>nul | findstr "RUNNING" >nul && echo   Estado: CORRIENDO || echo   Estado: DETENIDO
echo.
echo Servidor Flask:
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul && echo   Estado: CORRIENDO (puerto 5000) || echo   Estado: DETENIDO
echo.
echo Base de datos:
"%~dp0backend\venv\Scripts\python.exe" -c "import psycopg2; conn=psycopg2.connect(dbname='bienestar_estudiantil',user='postgres',password='sena2024',host='127.0.0.1',port='5432',connect_timeout=3); cur=conn.cursor(); cur.execute('SELECT count(*) FROM usuarios'); print(f'   Usuarios en DB: {cur.fetchone()[0]}'); cur.execute('SELECT count(*) FROM actividades'); print(f'   Actividades: {cur.fetchone()[0]}'); cur.execute('SELECT count(*) FROM programaciones'); print(f'   Programaciones: {cur.fetchone()[0]}'); cur.close(); conn.close()" 2>nul || echo   No se pudo conectar a la base de datos
echo.
echo ============================================
echo.
pause
goto menu

:salir
exit
