# Windows Deployment Guide - SPMVV Exam Results

This guide covers deploying the SPMVV Exam Results application on **Windows** using Docker Desktop.

---

## Prerequisites

### Required Software
1. **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop
   - Version: 4.0 or higher
   - Ensure WSL 2 backend is enabled (default on Windows 10/11)

2. **Git for Windows** (optional, for cloning repository)
   - Download: https://git-scm.com/download/win

3. **System Requirements**
   - Windows 10/11 (64-bit)
   - 4GB RAM minimum (8GB recommended)
   - 20GB free disk space
   - Internet connection for downloading images

---

## Quick Start

### Option 1: Using Command Prompt (Recommended)

1. **Open Command Prompt** (Win+R, type `cmd`, press Enter)

2. **Navigate to project directory**
   ```cmd
   cd C:\path\to\spmvv-exam-results
   ```

3. **Run deployment script**
   ```cmd
   windows\deploy_windows.bat
   ```

4. **Access the application**
   - Frontend: http://localhost:2026
   - Backend API: http://localhost:8000/api
   - Login: `admin` / `SpmvvExamResults`

### Option 2: Using PowerShell

1. **Open PowerShell** (Win+X, select "Windows PowerShell")

2. **Navigate to project directory**
   ```powershell
   cd C:\path\to\spmvv-exam-results
   ```

3. **Run deployment script**
   ```powershell
   .\windows\deploy_windows.ps1
   ```

4. **Access the application** (same URLs as above)

---

## Deployment Scripts

### `deploy_windows.bat` - Command Prompt Script
- Works from any directory (auto-detects project location)
- Validates Docker installation
- Automatic retry logic for frontend builds
- Full error handling
- Deployment time: 5-10 minutes

**Features:**
- Stops and removes old containers
- Creates Docker network
- Deploys database, backend, frontend
- Waits for services to be ready
- Displays access URLs

### `deploy_windows.ps1` - PowerShell Script
- Modern PowerShell with colored output
- Same functionality as .bat script
- Better error messages
- Progress indicators

**Choose based on preference:**
- Command Prompt users: Use `.bat`
- PowerShell users: Use `.ps1`

Both scripts produce identical results!

---

## Deployment Steps (What the Scripts Do)

### 1. Environment Setup
- Verifies Docker is installed and running
- Checks project directory structure
- Sets project name to `spmvv`

### 2. Cleanup Old Deployment
```cmd
docker stop spmvv_frontend spmvv_backend spmvv_db
docker rm spmvv_frontend spmvv_backend spmvv_db
```

### 3. Create Docker Network
```cmd
docker network create spmvv_network
```

### 4. Deploy Database (MariaDB)
```cmd
docker run -d ^
  --name spmvv_db ^
  --network spmvv_network ^
  -e MYSQL_ROOT_PASSWORD=RootPassword@2026 ^
  -e MYSQL_DATABASE=spmvv_results ^
  -e MYSQL_USER=spmvv_user ^
  -e MYSQL_PASSWORD=SpmvvDb@2026 ^
  -v spmvv_mysql_data:/var/lib/mysql ^
  -p 3306:3306 ^
  mariadb:10.11
```

**Wait 30 seconds** for database initialization.

### 5. Build & Deploy Backend (Django)
```cmd
cd backend
docker build -t spmvv_backend .
docker run -d ^
  --name spmvv_backend ^
  --network spmvv_network ^
  -e DB_HOST=spmvv_db ^
  -e DB_NAME=spmvv_results ^
  -e DB_USER=spmvv_user ^
  -e DB_PASSWORD=SpmvvDb@2026 ^
  -e DB_PORT=3306 ^
  -p 8000:8000 ^
  spmvv_backend
```

**Wait 20 seconds** for migrations and admin user creation.

### 6. Build & Deploy Frontend (React)
```cmd
cd frontend
docker build -t spmvv_frontend .
docker run -d ^
  --name spmvv_frontend ^
  --network spmvv_network ^
  -p 2026:80 ^
  spmvv_frontend
```

**Total deployment time:** 5-10 minutes (depending on internet speed)

---

## Accessing the Application

### Frontend (User Interface)
- **URL:** http://localhost:2026
- **Default Login:**
  - Username: `admin`
  - Password: `SpmvvExamResults`

### Backend API (REST API)
- **URL:** http://localhost:8000/api
- **Admin Panel:** http://localhost:8000/admin
- **API Documentation:** http://localhost:8000/api/docs

### Database (MariaDB)
- **Host:** localhost
- **Port:** 3306
- **Database:** spmvv_results
- **User:** spmvv_user
- **Password:** SpmvvDb@2026
- **Root Password:** RootPassword@2026

**Connect using MySQL Workbench or any MySQL client:**
```
Host: 127.0.0.1
Port: 3306
User: spmvv_user
Password: SpmvvDb@2026
Database: spmvv_results
```

---

## Manual Deployment (Without Scripts)

If you prefer to run commands manually:

### Step 1: Create Network
```cmd
docker network create spmvv_network
```

### Step 2: Start Database
```cmd
docker run -d --name spmvv_db --network spmvv_network -e MYSQL_ROOT_PASSWORD=RootPassword@2026 -e MYSQL_DATABASE=spmvv_results -e MYSQL_USER=spmvv_user -e MYSQL_PASSWORD=SpmvvDb@2026 -v spmvv_mysql_data:/var/lib/mysql -p 3306:3306 mariadb:10.11
```

Wait 30 seconds, then continue.

### Step 3: Build & Run Backend
```cmd
cd backend
docker build -t spmvv_backend .
docker run -d --name spmvv_backend --network spmvv_network -e DB_HOST=spmvv_db -e DB_NAME=spmvv_results -e DB_USER=spmvv_user -e DB_PASSWORD=SpmvvDb@2026 -e DB_PORT=3306 -p 8000:8000 spmvv_backend
cd ..
```

Wait 20 seconds, then continue.

### Step 4: Build & Run Frontend
```cmd
cd frontend
docker build -t spmvv_frontend .
docker run -d --name spmvv_frontend --network spmvv_network -p 2026:80 spmvv_frontend
cd ..
```

---

## Troubleshooting

### Docker Desktop Not Running
**Error:** `error during connect: This error may indicate that the docker daemon is not running`

**Solution:**
1. Open Docker Desktop from Start menu
2. Wait for Docker engine to start (whale icon in system tray)
3. Run deployment script again

### Port Already in Use
**Error:** `Bind for 0.0.0.0:2026 failed: port is already allocated`

**Solution:**
```cmd
REM Check what's using the port
netstat -ano | findstr :2026

REM Stop the conflicting container
docker stop spmvv_frontend
docker rm spmvv_frontend

REM Or change the port in docker run command
docker run -d --name spmvv_frontend --network spmvv_network -p 3000:80 spmvv_frontend
```

### Frontend Build Fails
**Error:** `ENOSPC: no space left on device` or timeout

**Solution:**
```cmd
REM Increase Docker memory in Docker Desktop settings
REM Settings > Resources > Advanced > Memory: 4GB or higher

REM Clear Docker build cache
docker builder prune -a

REM Retry build with no cache
docker build --no-cache -t spmvv_frontend .
```

### Cannot Access http://localhost:2026
**Error:** Site cannot be reached

**Solution:**
```cmd
REM Check if container is running
docker ps | findstr spmvv_frontend

REM Check container logs
docker logs spmvv_frontend

REM Restart container
docker restart spmvv_frontend

REM Check if port mapping is correct
docker port spmvv_frontend
```

### Database Connection Failed
**Error:** Backend logs show `Can't connect to MySQL server`

**Solution:**
```cmd
REM Check if database is running
docker ps | findstr spmvv_db

REM Check database logs
docker logs spmvv_db

REM Verify database is ready
docker exec spmvv_db mysql -uspmvv_user -pSpmvvDb@2026 -e "SHOW DATABASES;"

REM Restart backend after database is ready
docker restart spmvv_backend
```

---

## Managing the Application

### Check Container Status
```cmd
docker ps
```

**Expected output:**
```
CONTAINER ID   IMAGE              STATUS         PORTS                    NAMES
xxxxxxxxx      spmvv_frontend     Up 5 minutes   0.0.0.0:2026->80/tcp     spmvv_frontend
xxxxxxxxx      spmvv_backend      Up 5 minutes   0.0.0.0:8000->8000/tcp   spmvv_backend
xxxxxxxxx      mariadb:10.11      Up 6 minutes   0.0.0.0:3306->3306/tcp   spmvv_db
```

### View Logs
```cmd
REM View all logs
docker logs spmvv_frontend
docker logs spmvv_backend
docker logs spmvv_db

REM Follow logs in real-time
docker logs -f spmvv_frontend

REM View last 50 lines
docker logs --tail 50 spmvv_backend
```

### Restart Containers
```cmd
REM Restart individual container
docker restart spmvv_frontend

REM Restart all containers
docker restart spmvv_frontend spmvv_backend spmvv_db
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

### Complete Cleanup (Remove Everything)
```cmd
REM Stop and remove containers
docker stop spmvv_frontend spmvv_backend spmvv_db
docker rm spmvv_frontend spmvv_backend spmvv_db

REM Remove images
docker rmi spmvv_frontend spmvv_backend

REM Remove network
docker network rm spmvv_network

REM Remove database volume (WARNING: Deletes all data!)
docker volume rm spmvv_mysql_data
```

---

## Database Backup & Restore

### Backup Database
```cmd
REM Create backup directory
mkdir backups

REM Export database
docker exec spmvv_db mysqldump -uspmvv_user -pSpmvvDb@2026 spmvv_results > backups\backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.sql
```

### Restore Database
```cmd
REM Import database
docker exec -i spmvv_db mysql -uspmvv_user -pSpmvvDb@2026 spmvv_results < backups\backup_20260210.sql

REM Restart backend
docker restart spmvv_backend
```

---

## Updating the Application

### Update Frontend Code
```cmd
cd frontend

REM Make code changes in src/

REM Rebuild image
docker build -t spmvv_frontend .

REM Stop old container
docker stop spmvv_frontend
docker rm spmvv_frontend

REM Start new container
docker run -d --name spmvv_frontend --network spmvv_network -p 2026:80 spmvv_frontend

cd ..
```

### Update Backend Code
```cmd
cd backend

REM Make code changes

REM Rebuild image
docker build -t spmvv_backend .

REM Stop old container
docker stop spmvv_backend
docker rm spmvv_backend

REM Start new container with migrations
docker run -d --name spmvv_backend --network spmvv_network -e DB_HOST=spmvv_db -e DB_NAME=spmvv_results -e DB_USER=spmvv_user -e DB_PASSWORD=SpmvvDb@2026 -e DB_PORT=3306 -p 8000:8000 spmvv_backend

cd ..
```

**Or simply re-run the deployment script:**
```cmd
windows\deploy_windows.bat
```

---

## Performance Optimization

### Increase Docker Resources
1. Open Docker Desktop
2. Go to Settings > Resources > Advanced
3. Adjust:
   - **CPUs:** 4 or more
   - **Memory:** 4GB or more
   - **Swap:** 1GB or more
   - **Disk image size:** 64GB or more
4. Click "Apply & Restart"

### Clear Build Cache
```cmd
REM Remove unused images
docker image prune -a

REM Remove build cache
docker builder prune -a

REM Remove unused volumes
docker volume prune
```

### Monitor Resource Usage
```cmd
REM View container resource usage
docker stats

REM View disk usage
docker system df
```

---

## Security Considerations

### Change Default Passwords
**IMPORTANT:** The default passwords are hardcoded for development. For production:

1. **Database Passwords**
   - Edit `backend/Dockerfile` environment variables
   - Update MariaDB root password
   - Update database user password

2. **Admin User Password**
   - Edit `backend/init_admin.py`
   - Change `admin_password` variable
   - Rebuild backend image

3. **Django Secret Key**
   - Edit `backend/settings.py`
   - Generate new SECRET_KEY
   - Rebuild backend image

### Network Security
```cmd
REM Expose only frontend port externally
REM Remove -p flags from backend and database containers
REM Access them only through Docker network
```

### Enable HTTPS
```cmd
REM Use a reverse proxy (nginx, Traefik)
REM Generate SSL certificates (Let's Encrypt)
REM Configure proxy to forward to containers
```

---

## Differences from Linux Deployment

| Feature | Windows (Docker Desktop) | Linux VM (Podman) |
|---------|--------------------------|-------------------|
| Container Engine | Docker Desktop | Podman (docker CLI alias) |
| Script Format | `.bat` / `.ps1` | `.sh` (bash) |
| Line Endings | CRLF (`\r\n`) | LF (`\n`) |
| Path Separator | Backslash (`\`) | Forward slash (`/`) |
| Network Host | `host.docker.internal` | `localhost` |
| Volume Location | WSL filesystem | Native filesystem |
| Performance | WSL2 overhead | Native Linux |

**Functionality:** Identical application behavior on both platforms!

---

## FAQ

### Can I use Docker Compose instead?
Yes! Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  db:
    image: mariadb:10.11
    container_name: spmvv_db
    environment:
      MYSQL_ROOT_PASSWORD: RootPassword@2026
      MYSQL_DATABASE: spmvv_results
      MYSQL_USER: spmvv_user
      MYSQL_PASSWORD: SpmvvDb@2026
    volumes:
      - spmvv_mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    networks:
      - spmvv_network

  backend:
    build: ./backend
    container_name: spmvv_backend
    environment:
      DB_HOST: spmvv_db
      DB_NAME: spmvv_results
      DB_USER: spmvv_user
      DB_PASSWORD: SpmvvDb@2026
      DB_PORT: 3306
    ports:
      - "8000:8000"
    depends_on:
      - db
    networks:
      - spmvv_network

  frontend:
    build: ./frontend
    container_name: spmvv_frontend
    ports:
      - "2026:80"
    depends_on:
      - backend
    networks:
      - spmvv_network

volumes:
  spmvv_mysql_data:

networks:
  spmvv_network:
```

Deploy with: `docker-compose up -d`

### Can I run this on macOS?
Yes! Use `deploy_windows.sh` (rename from Linux version) or Docker Compose.

### How do I access from other computers?
Replace `localhost` with your Windows machine's IP address:
```
http://192.168.1.100:2026
```

**Firewall:** Allow inbound TCP ports 2026, 8000, 3306

### Can I change the ports?
Yes! Modify the `-p` flags in deployment scripts:
```cmd
REM Change frontend port from 2026 to 3000
docker run -d --name spmvv_frontend --network spmvv_network -p 3000:80 spmvv_frontend
```

Access at http://localhost:3000

---

## Support

### Documentation
- Main README: `README.md` (Linux deployment)
- Windows Guide: `windows/WINDOWS_README.md` (this file)

### Logs Location
- Container logs: `docker logs <container_name>`
- Docker Desktop logs: Settings > Troubleshoot > Get support

### Common Commands Reference
```cmd
REM Deploy application
windows\deploy_windows.bat

REM Check status
docker ps

REM View logs
docker logs -f spmvv_frontend

REM Restart service
docker restart spmvv_backend

REM Stop application
docker stop spmvv_frontend spmvv_backend spmvv_db

REM Clean up
docker rm spmvv_frontend spmvv_backend spmvv_db
docker network rm spmvv_network
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│         Windows 10/11 Host                  │
│  ┌───────────────────────────────────────┐  │
│  │      Docker Desktop (WSL2)            │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │   spmvv_network (bridge)        │  │  │
│  │  │                                 │  │  │
│  │  │  ┌──────────┐  ┌──────────┐   │  │  │
│  │  │  │Frontend  │  │Backend   │   │  │  │
│  │  │  │React+Vite│  │Django+DRF│   │  │  │
│  │  │  │Port:2026 │  │Port:8000 │   │  │  │
│  │  │  └────┬─────┘  └────┬─────┘   │  │  │
│  │  │       │             │          │  │  │
│  │  │       └──────┬──────┘          │  │  │
│  │  │              │                 │  │  │
│  │  │         ┌────┴─────┐           │  │  │
│  │  │         │ MariaDB  │           │  │  │
│  │  │         │Port:3306 │           │  │  │
│  │  │         │Volume:DB │           │  │  │
│  │  │         └──────────┘           │  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## Project Structure

```
spmvv-exam-results/
├── backend/
│   ├── Dockerfile              # Backend container build
│   ├── requirements.txt        # Python dependencies
│   ├── manage.py               # Django management
│   ├── init_admin.py           # Admin user creation
│   ├── results/                # Django app
│   └── backend/                # Django project settings
├── frontend/
│   ├── Dockerfile              # Frontend container build
│   ├── package.json            # Node dependencies
│   ├── vite.config.js          # Vite configuration
│   ├── nginx.conf              # Nginx web server config
│   ├── public/                 # Static assets
│   └── src/                    # React source code
├── windows/
│   ├── deploy_windows.bat      # Command Prompt deployment
│   ├── deploy_windows.ps1      # PowerShell deployment
│   └── WINDOWS_README.md       # This file
├── backups/                    # Database backups (optional)
└── README.md                   # Main documentation (Linux)
```

---

## Quick Reference Card

### First Time Setup
1. Install Docker Desktop
2. Clone/download project
3. Open Command Prompt
4. Run `windows\deploy_windows.bat`
5. Wait 5-10 minutes
6. Access http://localhost:2026

### Daily Usage
- **Start:** `docker start spmvv_db spmvv_backend spmvv_frontend`
- **Stop:** `docker stop spmvv_frontend spmvv_backend spmvv_db`
- **Status:** `docker ps`
- **Logs:** `docker logs -f spmvv_frontend`

### Updating
1. Make code changes
2. Run `windows\deploy_windows.bat`
3. Wait for rebuild
4. Refresh browser

### Troubleshooting
1. Check Docker Desktop is running
2. Check container logs: `docker logs <container>`
3. Restart container: `docker restart <container>`
4. Re-run deployment script

---

**Version:** 1.0  
**Last Updated:** February 10, 2026  
**Platform:** Windows 10/11 with Docker Desktop

For Linux deployment, see main `README.md` file.
