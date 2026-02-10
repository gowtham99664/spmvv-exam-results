# SPMVV Exam Results - Windows Deployment

Deploy the SPMVV Exam Results application on Windows using Docker Desktop.

---

## Prerequisites

1. **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop
   - Version: 4.0 or higher
   - Ensure it's running before deployment

2. **System Requirements**
   - Windows 10/11 (64-bit)
   - 4GB RAM minimum (8GB recommended)
   - 20GB free disk space

---

## Quick Start

### 1. Copy Project Files
Copy the entire `spmvv-exam-results` folder to your Windows machine:
```
C:\spmvv-exam-results\
```

### 2. Run Deployment
Double-click the batch file or run from Command Prompt:
```cmd
cd C:\spmvv-exam-results
deploy_windows.bat
```

### 3. Wait for Deployment
- Database: ~30 seconds
- Backend: ~1-2 minutes
- Frontend: ~5-10 minutes (npm install is slow)
- **Total time: 8-15 minutes**

### 4. Access Application
- **Frontend:** http://localhost:2026
- **Username:** admin
- **Password:** SpmvvExamResults

---

## What the Script Does

```
[STEP 1/5] Cleanup old containers
[STEP 2/5] Create Docker network
[STEP 3/5] Deploy MariaDB database
[STEP 4/5] Build and deploy Django backend
[STEP 5/5] Build and deploy React frontend
```

---

## Troubleshooting

### Docker Not Running
**Error:** `Docker is not running!`

**Solution:**
1. Open Docker Desktop from Start menu
2. Wait for Docker engine to start (whale icon in system tray)
3. Run `deploy_windows.bat` again

---

### Port Already in Use
**Error:** `Bind for 0.0.0.0:2026 failed: port is already allocated`

**Solution:**
```cmd
REM Stop the container using the port
docker stop spmvv_frontend
docker rm spmvv_frontend

REM Or kill the process
netstat -ano | findstr :2026
taskkill /F /PID <process_id>
```

---

### Frontend Build Fails
**Error:** Build timeout or memory issues

**Solution:**
1. Open Docker Desktop
2. Go to Settings → Resources → Advanced
3. Increase **Memory to 4GB or more**
4. Click "Apply & Restart"
5. Run `deploy_windows.bat` again

---

### Cannot Access http://localhost:2026
**Error:** Site cannot be reached

**Solution:**
```cmd
REM Check if containers are running
docker ps

REM Check frontend logs
docker logs spmvv_frontend

REM Restart frontend
docker restart spmvv_frontend
```

---

## Managing Containers

### Check Status
```cmd
docker ps
```

### View Logs
```cmd
docker logs -f spmvv_frontend
docker logs -f spmvv_backend
docker logs -f spmvv_db
```

### Restart Containers
```cmd
REM Restart single container
docker restart spmvv_backend

REM Restart all
docker restart spmvv_db spmvv_backend spmvv_frontend
```

### Stop Application
```cmd
docker stop spmvv_frontend spmvv_backend spmvv_db
```

### Start Stopped Containers
```cmd
docker start spmvv_db
timeout /t 10
docker start spmvv_backend
timeout /t 10
docker start spmvv_frontend
```

### Complete Cleanup
```cmd
REM Stop and remove everything
docker stop spmvv_frontend spmvv_backend spmvv_db
docker rm spmvv_frontend spmvv_backend spmvv_db
docker network rm spmvv_network
docker volume rm spmvv_mysql_data

REM Remove images
docker rmi spmvv-frontend spmvv-backend mariadb:10.11
```

---

## Database Backup

### Export Database
```cmd
docker exec spmvv_db mysqldump -uspmvv_user -pSpmvvDb@2026 spmvv_results > backup.sql
```

### Import Database
```cmd
docker exec -i spmvv_db mysql -uspmvv_user -pSpmvvDb@2026 spmvv_results < backup.sql
docker restart spmvv_backend
```

---

## Updating Code

After making changes to code:

```cmd
cd C:\spmvv-exam-results
deploy_windows.bat
```

The script will rebuild the changed components automatically.

---

## Configuration

Edit these values in `deploy_windows.bat` if needed:

```batch
set DB_NAME=spmvv_results
set DB_USER=spmvv_user
set DB_PASSWORD=SpmvvDb@2026
set MYSQL_ROOT_PASSWORD=RootPassword@2026
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=SpmvvExamResults
```

**WARNING:** For production, change all default passwords!

---

## Access from Other Computers

To access from other machines on your network:

1. Find your Windows machine's IP:
   ```cmd
   ipconfig
   ```

2. Access using the IP:
   ```
   http://192.168.1.100:2026
   ```

3. Allow port in Windows Firewall:
   ```cmd
   netsh advfirewall firewall add rule name="SPMVV Frontend" dir=in action=allow protocol=TCP localport=2026
   netsh advfirewall firewall add rule name="SPMVV Backend" dir=in action=allow protocol=TCP localport=8000
   ```

---

## Architecture

```
┌──────────────────────────────────────┐
│     Windows Machine (localhost)      │
│  ┌────────────────────────────────┐  │
│  │    Docker Desktop (WSL2)       │  │
│  │  ┌──────────────────────────┐  │  │
│  │  │  spmvv_network (bridge)  │  │  │
│  │  │                          │  │  │
│  │  │  ┌─────────────────┐    │  │  │
│  │  │  │   Frontend      │    │  │  │
│  │  │  │   React + Vite  │    │  │  │
│  │  │  │   Port: 2026    │    │  │  │
│  │  │  └────────┬────────┘    │  │  │
│  │  │           │             │  │  │
│  │  │  ┌────────┴────────┐    │  │  │
│  │  │  │   Backend       │    │  │  │
│  │  │  │   Django + DRF  │    │  │  │
│  │  │  │   Port: 8000    │    │  │  │
│  │  │  └────────┬────────┘    │  │  │
│  │  │           │             │  │  │
│  │  │  ┌────────┴────────┐    │  │  │
│  │  │  │   Database      │    │  │  │
│  │  │  │   MariaDB 10.11 │    │  │  │
│  │  │  │   Port: 3306    │    │  │  │
│  │  │  └─────────────────┘    │  │  │
│  │  └──────────────────────────┘  │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Deploy | `deploy_windows.bat` |
| Check status | `docker ps` |
| View logs | `docker logs -f spmvv_frontend` |
| Stop all | `docker stop spmvv_db spmvv_backend spmvv_frontend` |
| Start all | `docker start spmvv_db spmvv_backend spmvv_frontend` |
| Access app | http://localhost:2026 |

---

## Differences from Linux Deployment

| Feature | Windows (Docker Desktop) | Linux VM |
|---------|-------------------------|----------|
| Script | `deploy_windows.bat` | `deploy_simple.sh` |
| Server | localhost | 10.127.248.83 |
| Line endings | CRLF | LF |
| Container engine | Docker Desktop | Podman |
| Access URL | http://localhost:2026 | http://10.127.248.83:2026 |

---

**Version:** 1.0  
**Date:** February 10, 2026  
**Platform:** Windows 10/11 + Docker Desktop

For Linux deployment, see main `README.md` file.
