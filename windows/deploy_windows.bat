@echo off
REM SPMVV Deployment Script for Windows Docker Desktop
REM This script works from any directory where you placed the code

echo ========================================
echo SPMVV Deployment for Windows
echo ========================================
echo.

REM Get current directory (where this script is located)
set PROJECT_DIR=%~dp0
set PROJECT_DIR=%PROJECT_DIR:~0,-1%

echo Project directory: %PROJECT_DIR%
echo.

REM Configuration
set SERVER_IP=localhost

REM Database credentials
set DB_NAME=spmvv_results
set DB_USER=spmvv_user
set DB_PASSWORD=SpmvvDb@2026
set MYSQL_ROOT_PASSWORD=RootPassword@2026

REM Admin credentials
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=SpmvvExamResults

echo [1/5] Cleanup old containers...
docker stop spmvv_backend spmvv_frontend spmvv_db 2>nul
docker rm -f spmvv_backend spmvv_frontend spmvv_db 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/5] Creating network...
docker network create spmvv_network 2>nul

echo.
echo [3/5] Starting database...
docker run -d --name spmvv_db --network spmvv_network -p 3306:3306 -e MYSQL_ROOT_PASSWORD=%MYSQL_ROOT_PASSWORD% -e MYSQL_DATABASE=%DB_NAME% -e MYSQL_USER=%DB_USER% -e MYSQL_PASSWORD=%DB_PASSWORD% -v spmvv_mysql_data:/var/lib/mysql mariadb:10.11

echo   Waiting 20 seconds for database...
timeout /t 20 /nobreak >nul

echo.
echo [4/5] Building and starting backend...
cd /d "%PROJECT_DIR%\backend"
if not exist "Dockerfile" (
    echo   ERROR: backend/Dockerfile not found!
    echo   Make sure you are running this script from the project root directory.
    pause
    exit /b 1
)

docker build -t spmvv-backend .
if errorlevel 1 (
    echo   Backend build failed!
    pause
    exit /b 1
)

docker run -d --name spmvv_backend --network spmvv_network -p 8000:8000 -e SECRET_KEY=django-insecure-windows -e DEBUG=True -e ALLOWED_HOSTS=localhost,127.0.0.1,%SERVER_IP% -e DB_ENGINE=django.db.backends.mysql -e DB_NAME=%DB_NAME% -e DB_USER=%DB_USER% -e DB_PASSWORD=%DB_PASSWORD% -e DB_HOST=spmvv_db -e DB_PORT=3306 -e ADMIN_USERNAME=%ADMIN_USERNAME% -e ADMIN_DEFAULT_PASSWORD=%ADMIN_PASSWORD% -e CORS_ALLOWED_ORIGINS=http://localhost:2026,http://127.0.0.1:2026 spmvv-backend:latest

echo   Waiting 10 seconds for backend...
timeout /t 10 /nobreak >nul

echo.
echo [5/5] Building and starting frontend...
cd /d "%PROJECT_DIR%\frontend"
if not exist "Dockerfile" (
    echo   ERROR: frontend/Dockerfile not found!
    echo   Make sure you are running this script from the project root directory.
    pause
    exit /b 1
)

docker build --build-arg VITE_API_URL=http://localhost:8000/api -t spmvv-frontend .
if errorlevel 1 (
    echo   Frontend build failed! Retrying...
    docker build --no-cache --build-arg VITE_API_URL=http://localhost:8000/api -t spmvv-frontend .
)

docker run -d --name spmvv_frontend --network spmvv_network -p 2026:2026 -e VITE_API_URL=http://localhost:8000/api spmvv-frontend:latest

echo   Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo   DEPLOYMENT COMPLETE
echo ========================================
echo.
docker ps
echo.
echo Frontend: http://localhost:2026
echo Backend:  http://localhost:8000/api
echo Login: %ADMIN_USERNAME% / %ADMIN_PASSWORD%
echo.
pause
