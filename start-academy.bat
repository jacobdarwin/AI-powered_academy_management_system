@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%academy-backend"
set "BACKEND_URL=http://127.0.0.1:5000"

if not exist "%BACKEND_DIR%\wsgi.py" (
    echo Backend folder not found: "%BACKEND_DIR%"
    pause
    exit /b 1
)

start "Academy Backend + Frontend" cmd /k "cd /d "%BACKEND_DIR%" && py -m flask --app wsgi.py run --host 127.0.0.1 --port 5000"

timeout /t 3 /nobreak >nul
start "" "%BACKEND_URL%/"

echo Academy started.
echo Frontend: %BACKEND_URL%/
echo API: %BACKEND_URL%/api/v1
endlocal
