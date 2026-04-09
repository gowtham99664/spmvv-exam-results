@echo off
REM =============================================================================
REM SPMVV Exam Results - Windows Docker Desktop Deployment
REM =============================================================================
REM Run this script on Windows machine with Docker Desktop installed
REM The application will be accessible at http://localhost:2026
REM =============================================================================

setlocal enabledelayedexpansion

REM Configuration
set PROJECT_NAME=spmvv
set DB_NAME=spmvv_results
set DB_USER=spmvv_user
set DB_PASSWORD=SpmvvDb@2026
set MYSQL_ROOT_PASSWORD=RootPassword@2026
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=SpmvvExamResults
set SERVER_IP=localhost

REM Get project directory (where this batch file is located)
set PROJECT_DIR=%~dp0
set PROJECT_DIR=%PROJECT_DIR:~0,-1%

echo ===============================================================================
echo                    SPMVV Exam Results - Windows Deployment
echo ===============================================================================
echo.
echo Project: SPMVV Exam Results Application
echo Location: %PROJECT_DIR%
echo Server: %SERVER_IP%
echo Time: %date% %time%
echo.
echo ===============================================================================
echo.

REM Check if Docker is running
echo [CHECK] Verifying Docker Desktop...
call docker ps >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo   - Docker Desktop is running
echo.

REM =============================================================================
REM Step 1: Detect fresh vs redeployment
REM =============================================================================
echo [STEP 1/9] Detecting deployment type...
set IS_REDEPLOYMENT=false
set BACKUP_FILE=

docker ps -a --format "{{.Names}}" 2>nul | findstr /i "%PROJECT_NAME%_db" >nul 2>&1
if !errorlevel! equ 0 set IS_REDEPLOYMENT=true

docker ps -a --format "{{.Names}}" 2>nul | findstr /i "%PROJECT_NAME%_backend" >nul 2>&1
if !errorlevel! equ 0 set IS_REDEPLOYMENT=true

if "%IS_REDEPLOYMENT%"=="true" (
    echo   - Existing deployment detected. This is a REDEPLOYMENT.
) else (
    echo   - No existing containers found. This is a FRESH deployment.
)
echo.

REM =============================================================================
REM Step 2: Backup database if redeploying
REM =============================================================================
echo [STEP 2/9] Database backup...
if "%IS_REDEPLOYMENT%"=="false" goto :skip_backup

docker ps --format "{{.Names}}" 2>nul | findstr /i "%PROJECT_NAME%_db" >nul 2>&1
if !errorlevel! neq 0 (
    echo   - Database container not running. Skipping backup.
    goto :skip_backup
)

echo   - Backing up existing database...
if not exist "%PROJECT_DIR%\backups" mkdir "%PROJECT_DIR%\backups"

REM Generate timestamp for backup filename
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set dt=%%I
set BACKUP_FILE=%PROJECT_DIR%\backups\db_backup_%dt:~0,14%.sql

call docker exec %PROJECT_NAME%_db mysqldump -u %DB_USER% -p%DB_PASSWORD% %DB_NAME% > "%BACKUP_FILE%" 2>nul
if !errorlevel! neq 0 (
    echo   - WARNING: Backup failed. Continuing without backup.
    set BACKUP_FILE=
) else (
    echo   - Database backed up to: %BACKUP_FILE%
)

:skip_backup
echo   - Backup step complete
echo.

REM =============================================================================
REM Step 3: Stop and remove old containers and images (force fresh build)
REM =============================================================================
echo [STEP 3/9] Cleaning up old containers and images...
call docker stop %PROJECT_NAME%_backend %PROJECT_NAME%_frontend %PROJECT_NAME%_db %PROJECT_NAME%_ollama 2>nul
call docker rm -f %PROJECT_NAME%_backend %PROJECT_NAME%_frontend %PROJECT_NAME%_db %PROJECT_NAME%_ollama 2>nul
echo   - Old containers removed
echo   - Removing old backend and frontend images (force fresh build)...
call docker rmi %PROJECT_NAME%-backend:latest 2>nul
call docker rmi %PROJECT_NAME%-frontend:latest 2>nul
echo   - Old images removed

REM If this is a fresh deployment (or previous deploy failed), wipe database volume
REM to ensure clean migrations from scratch
if "%IS_REDEPLOYMENT%"=="false" (
    echo   - Removing old database volume for clean start...
    call docker volume rm %PROJECT_NAME%_mysql_data 2>nul
)
echo.

REM =============================================================================
REM Step 4: Network
REM =============================================================================
echo [STEP 4/9] Setting up Docker network...
call docker network inspect %PROJECT_NAME%_network >nul 2>&1
if !errorlevel! neq 0 (
    echo   - Creating network...
    call docker network create %PROJECT_NAME%_network
) else (
    echo   - Network already exists
)
echo   - Network ready
echo.

REM =============================================================================
REM Step 5: Database
REM =============================================================================
echo [STEP 5/9] Deploying database...
call docker run -d --name %PROJECT_NAME%_db ^
  --network %PROJECT_NAME%_network ^
  -e MYSQL_ROOT_PASSWORD=%MYSQL_ROOT_PASSWORD% ^
  -e MYSQL_DATABASE=%DB_NAME% ^
  -e MYSQL_USER=%DB_USER% ^
  -e MYSQL_PASSWORD=%DB_PASSWORD% ^
  -v %PROJECT_NAME%_mysql_data:/var/lib/mysql ^
  -p 3306:3306 ^
  mariadb:10.11

if !errorlevel! neq 0 (
    echo ERROR: Failed to start database container
    pause
    exit /b 1
)

echo   - Waiting for database to initialize (30 seconds)...
timeout /t 30 /nobreak >nul

REM Restore backup if redeploying
if "%IS_REDEPLOYMENT%"=="false" goto :skip_restore
if "%BACKUP_FILE%"=="" goto :skip_restore

echo   - Restoring database from backup...
call docker exec -i %PROJECT_NAME%_db mysql -u %DB_USER% -p%DB_PASSWORD% %DB_NAME% < "%BACKUP_FILE%"
if !errorlevel! neq 0 (
    echo   - WARNING: Restore failed. Database will start fresh.
) else (
    echo   - Database restored successfully
)

:skip_restore
echo   - Database ready
echo.

REM =============================================================================
REM Step 6: Ollama AI container
REM =============================================================================
echo [STEP 6/9] Deploying Ollama AI container...
cd /d "%PROJECT_DIR%\ollama"

if not exist "Dockerfile" (
    echo ERROR: Ollama Dockerfile not found at %PROJECT_DIR%\ollama\Dockerfile
    pause
    exit /b 1
)

call docker image inspect %PROJECT_NAME%-ollama:latest >nul 2>&1
if !errorlevel! equ 0 (
    echo   - Ollama image already exists. Skipping build.
    goto :ollama_run
)

echo   - Building Ollama image (downloads qwen2.5:3b ~2GB, may take 5-10 min)...
call docker build -t %PROJECT_NAME%-ollama .
if !errorlevel! neq 0 (
    echo ERROR: Ollama image build failed!
    pause
    exit /b 1
)
echo   - Ollama image built

:ollama_run
call docker run -d --name %PROJECT_NAME%_ollama ^
  --network %PROJECT_NAME%_network ^
  -p 11434:11434 ^
  -e OLLAMA_HOST=0.0.0.0:11434 ^
  %PROJECT_NAME%-ollama:latest

if !errorlevel! neq 0 (
    echo ERROR: Failed to start Ollama container
    pause
    exit /b 1
)

echo   - Waiting for Ollama to be ready (15 seconds)...
timeout /t 15 /nobreak >nul
echo   - Ollama ready
echo.

REM =============================================================================
REM Step 7: Backend
REM =============================================================================
echo [STEP 7/9] Deploying backend...
cd /d "%PROJECT_DIR%\backend"

if not exist "Dockerfile" (
    echo ERROR: Backend Dockerfile not found at %PROJECT_DIR%\backend\Dockerfile
    pause
    exit /b 1
)

echo   - Building backend image (fresh, no cache)...
call docker build --no-cache -t %PROJECT_NAME%-backend .
if !errorlevel! neq 0 (
    echo ERROR: Backend build failed!
    pause
    exit /b 1
)

echo   - Starting backend container...
call docker run -d --name %PROJECT_NAME%_backend ^
  --network %PROJECT_NAME%_network ^
  -p 8000:8000 ^
  -v %PROJECT_NAME%_media_data:/app/media ^
  -e SECRET_KEY=django-insecure-docker-windows ^
  -e DEBUG=True ^
  -e ALLOWED_HOSTS=localhost,127.0.0.1 ^
  -e DB_ENGINE=django.db.backends.mysql ^
  -e DB_NAME=%DB_NAME% ^
  -e DB_USER=%DB_USER% ^
  -e DB_PASSWORD=%DB_PASSWORD% ^
  -e DB_HOST=%PROJECT_NAME%_db ^
  -e DB_PORT=3306 ^
  -e ADMIN_USERNAME=%ADMIN_USERNAME% ^
  -e ADMIN_DEFAULT_PASSWORD=%ADMIN_PASSWORD% ^
  -e CORS_ALLOWED_ORIGINS=http://localhost:2026,http://127.0.0.1:2026 ^
  -e CORS_EXTRA_ORIGINS=http://localhost:2026,http://127.0.0.1:2026 ^
  -e CSRF_EXTRA_ORIGINS=http://localhost:2026,http://127.0.0.1:2026 ^
  -e OLLAMA_URL=http://%PROJECT_NAME%_ollama:11434 ^
  %PROJECT_NAME%-backend:latest

if !errorlevel! neq 0 (
    echo ERROR: Failed to start backend container
    pause
    exit /b 1
)

echo   - Waiting for migrations (20 seconds)...
timeout /t 20 /nobreak >nul
echo   - Backend ready
echo.

REM =============================================================================
REM Step 8: Frontend (multi-stage Docker build - npm runs inside container)
REM =============================================================================
echo [STEP 8/9] Deploying frontend...
cd /d "%PROJECT_DIR%\frontend"

if not exist "Dockerfile" (
    echo ERROR: Frontend Dockerfile not found at %PROJECT_DIR%\frontend\Dockerfile
    pause
    exit /b 1
)

echo   - Building frontend image (multi-stage: npm install + build inside Docker)...
echo   - This may take a few minutes on first run...

REM Disable BuildKit to avoid unreliable exit codes on Windows
set DOCKER_BUILDKIT=0

call docker build -t %PROJECT_NAME%-frontend .

REM BuildKit on Windows can return non-zero even on success.
REM So we verify by checking if the image actually exists.
call docker image inspect %PROJECT_NAME%-frontend:latest >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: Frontend image build failed! Image not found.
    echo   Check the Docker build output above for errors.
    pause
    exit /b 1
)
echo   - Frontend image built successfully

echo   - Removing any leftover frontend container...
docker stop %PROJECT_NAME%_frontend >nul 2>&1
docker rm -f %PROJECT_NAME%_frontend >nul 2>&1

echo   - Starting frontend container...
call docker run -d --name %PROJECT_NAME%_frontend ^
  --network %PROJECT_NAME%_network ^
  -p 2026:2026 ^
  %PROJECT_NAME%-frontend:latest

if !errorlevel! neq 0 (
    echo ERROR: Failed to start frontend container
    pause
    exit /b 1
)

echo   - Waiting for startup (10 seconds)...
timeout /t 10 /nobreak >nul
echo   - Frontend ready
echo.

REM =============================================================================
REM Step 9: Verification
REM =============================================================================
echo [STEP 9/9] Verifying deployment...

echo   - Checking containers...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr %PROJECT_NAME%
echo.

echo   - Testing backend API...
curl -s -o nul -w "     Backend API: HTTP %%{http_code}" http://localhost:8000/api/login/ 2>nul
echo.

echo   - Testing frontend...
curl -s -o nul -w "     Frontend:    HTTP %%{http_code}" http://localhost:2026/ 2>nul
echo.
echo.

REM =============================================================================
REM Deployment Summary
REM =============================================================================
echo ===============================================================================
echo                         DEPLOYMENT COMPLETED
echo ===============================================================================
echo.
echo Access Information:
echo   Frontend URL:  http://localhost:2026
echo   Backend API:   http://localhost:8000/api
echo   Admin Panel:   http://localhost:8000/admin
echo   Ollama API:    http://localhost:11434
echo.
echo Login Credentials:
echo   Username:  %ADMIN_USERNAME%
echo   Password:  %ADMIN_PASSWORD%
echo.
if not "%BACKUP_FILE%"=="" (
    echo Backup saved to: %BACKUP_FILE%
    echo.
)
echo ===============================================================================
echo.
echo Useful Commands:
echo   Check status:  docker ps
echo   Backend logs:  docker logs -f %PROJECT_NAME%_backend
echo   Frontend logs: docker logs -f %PROJECT_NAME%_frontend
echo   Stop all:      docker stop %PROJECT_NAME%_db %PROJECT_NAME%_ollama %PROJECT_NAME%_backend %PROJECT_NAME%_frontend
echo   Start all:     docker start %PROJECT_NAME%_db && timeout /t 10 && docker start %PROJECT_NAME%_ollama %PROJECT_NAME%_backend %PROJECT_NAME%_frontend
echo.
echo ===============================================================================
echo Deployment completed at: %date% %time%
echo ===============================================================================
echo.

pause
