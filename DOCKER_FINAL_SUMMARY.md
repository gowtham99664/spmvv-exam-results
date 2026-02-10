# SPMVV Exam Results - Docker Deployment Summary

## ✅ Admin Credentials - VERIFIED AND CONFIGURED

**Default admin credentials are hardcoded in multiple places:**

### 1. Environment Variables (.env file)
```bash
ADMIN_USERNAME=admin
ADMIN_DEFAULT_PASSWORD=SpmvvExamResults
```

### 2. Docker Compose Configuration
```yaml
environment:
  - ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
  - ADMIN_DEFAULT_PASSWORD=${ADMIN_DEFAULT_PASSWORD:-SpmvvExamResults}
```

### 3. Django Management Command
The `init_admin.py` command reads from environment variables:
- `ADMIN_USERNAME` (default: admin)
- `ADMIN_DEFAULT_PASSWORD` (default: SpmvvExamResults)

**These credentials are consistent across all deployment methods!**

---

## 🐳 Docker Deployment - Final Working Commands

Your server uses **Podman** (Docker alternative). Here are the tested commands:

### Option 1: Manual Step-by-Step (RECOMMENDED - Most Reliable)

```bash
ssh root@10.127.248.83
cd /root/spmvv-exam-results

# 1. Stop old containers
podman stop spmvv_backend spmvv_frontend spmvv_db 2>/dev/null || true
podman rm spmvv_backend spmvv_frontend spmvv_db 2>/dev/null || true

# 2. Create network
podman network create spmvv_network 2>/dev/null || true

# 3. Start database
podman run -d \
  --name spmvv_db \
  --network spmvv_network \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=RootPassword@2026 \
  -e MYSQL_DATABASE=spmvv_results \
  -e MYSQL_USER=spmvv_user \
  -e MYSQL_PASSWORD=SpmvvDb@2026 \
  -v spmvv_mysql_data:/var/lib/mysql \
  docker.io/library/mariadb:10.11

# Wait for database (30 seconds)
sleep 30

# 4. Build and start backend
cd backend
podman build -t spmvv_backend:latest .

podman run -d \
  --name spmvv_backend \
  --network spmvv_network \
  -p 8000:8000 \
  -e SECRET_KEY=django-insecure-change-me \
  -e DEBUG=True \
  -e ALLOWED_HOSTS=localhost,127.0.0.1,10.127.248.83 \
  -e DB_ENGINE=django.db.backends.mysql \
  -e DB_NAME=spmvv_results \
  -e DB_USER=spmvv_user \
  -e DB_PASSWORD=SpmvvDb@2026 \
  -e DB_HOST=spmvv_db \
  -e DB_PORT=3306 \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_DEFAULT_PASSWORD=SpmvvExamResults \
  -e CORS_ALLOWED_ORIGINS=http://localhost:2026,http://10.127.248.83:2026 \
  spmvv_backend:latest

cd ..

# Wait for backend (20 seconds)
sleep 20

# 5. Build and start frontend
cd frontend
podman build -t spmvv_frontend:latest --build-arg VITE_API_URL=http://10.127.248.83:8000/api .

podman run -d \
  --name spmvv_frontend \
  --network spmvv_network \
  -p 2026:2026 \
  -e VITE_API_URL=http://10.127.248.83:8000/api \
  spmvv_frontend:latest

cd ..

# 6. Open firewall ports
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --permanent --add-port=2026/tcp
firewall-cmd --reload

# 7. Check status
podman ps
```

### Option 2: Using the Automated Script

```bash
ssh root@10.127.248.83
cd /root/spmvv-exam-results
./SIMPLE_DOCKER_DEPLOY.sh
```

---

## 🔍 Verify Admin Credentials Are Working

### 1. Check Backend Logs for Admin Creation
```bash
podman logs spmvv_backend | grep -i admin
```

**Expected output:**
```
Successfully created admin user: admin
Default password set. Please change it after first login!
```

### 2. Test Login API
```bash
curl -X POST http://10.127.248.83:8000/api/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"SpmvvExamResults"}'
```

**Expected output:**
```json
{"access":"<token>","refresh":"<token>"}
```

### 3. Test from Browser
1. Go to: `http://10.127.248.83:2026`
2. Login with:
   - Username: `admin`
   - Password: `SpmvvExamResults`

---

## 📊 Container Management

### Check Status
```bash
podman ps
```

**Expected output:**
```
CONTAINER ID  IMAGE                           STATUS      PORTS                   NAMES
xxxx          spmvv_frontend:latest           Up          0.0.0.0:2026->2026/tcp  spmvv_frontend
xxxx          spmvv_backend:latest            Up          0.0.0.0:8000->8000/tcp  spmvv_backend
xxxx          docker.io/library/mariadb:10.11 Up          0.0.0.0:3306->3306/tcp  spmvv_db
```

### View Logs
```bash
# All logs at once
podman logs spmvv_backend
podman logs spmvv_frontend
podman logs spmvv_db

# Follow logs in real-time
podman logs -f spmvv_backend
```

### Stop Containers
```bash
podman stop spmvv_backend spmvv_frontend spmvv_db
```

### Start Containers
```bash
podman start spmvv_db
sleep 10
podman start spmvv_backend
sleep 5
podman start spmvv_frontend
```

### Restart Containers
```bash
podman restart spmvv_backend spmvv_frontend
```

### Remove Containers
```bash
podman stop spmvv_backend spmvv_frontend spmvv_db
podman rm spmvv_backend spmvv_frontend spmvv_db
```

---

## 🔧 Troubleshooting

### Issue: Backend won't start
```bash
# Check logs
podman logs spmvv_backend

# Common causes:
# 1. Database not ready - wait 30 seconds after starting db
# 2. Database connection error - check DB_HOST=spmvv_db
# 3. Missing migrations - check logs for errors
```

### Issue: Frontend shows blank page
```bash
# Check if backend is accessible
curl http://localhost:8000/api/

# Check frontend logs
podman logs spmvv_frontend

# Verify VITE_API_URL
podman inspect spmvv_frontend | grep VITE_API_URL
```

### Issue: Login doesn't work
```bash
# Test API directly
curl -X POST http://localhost:8000/api/login/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"SpmvvExamResults"}'

# Check if admin user was created
podman exec spmvv_backend python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(username='admin').exists())"
```

### Issue: Can't access from browser
```bash
# Check firewall
firewall-cmd --list-ports

# Check if ports are open
netstat -tlnp | grep -E '(8000|2026)'

# Check containers are running
podman ps
```

---

## 🎯 Quick Reference

| Action | Command |
|--------|---------|
| **Deploy** | `./SIMPLE_DOCKER_DEPLOY.sh` |
| **Status** | `podman ps` |
| **Logs** | `podman logs -f spmvv_backend` |
| **Stop** | `podman stop spmvv_backend spmvv_frontend spmvv_db` |
| **Start** | `podman start spmvv_db && sleep 10 && podman start spmvv_backend spmvv_frontend` |
| **Restart** | `podman restart spmvv_backend spmvv_frontend` |
| **Remove** | `podman rm -f spmvv_backend spmvv_frontend spmvv_db` |
| **Shell** | `podman exec -it spmvv_backend bash` |
| **DB Shell** | `podman exec -it spmvv_db mysql -u spmvv_user -pSpmvvDb@2026 spmvv_results` |

---

## ✅ Admin Credentials - Final Confirmation

**These are HARDCODED and will ALWAYS be:**

```
Username: admin
Password: SpmvvExamResults
```

**Locations where this is defined:**
1. `/root/spmvv-exam-results/.env` → `ADMIN_USERNAME` and `ADMIN_DEFAULT_PASSWORD`
2. `docker-compose.yml` → environment variables
3. Backend Dockerfile → passes env vars to container
4. `backend/results/management/commands/init_admin.py` → reads from env vars

**The admin user is created automatically when the backend container starts!**

---

## 🚀 Ready to Deploy

Run this single command:

```bash
ssh root@10.127.248.83 'cd /root/spmvv-exam-results && ./SIMPLE_DOCKER_DEPLOY.sh'
```

Or follow the manual steps above.

**Login will work with:** `admin` / `SpmvvExamResults`

---

## Files on Server

All files are located at: `/root/spmvv-exam-results/`

Key files:
- `SIMPLE_DOCKER_DEPLOY.sh` - Simple deployment script
- `docker-compose.yml` - Container orchestration
- `.env` - Environment variables (admin credentials here)
- `backend/Dockerfile` - Backend container
- `frontend/Dockerfile` - Frontend container
- `DOCKER_DEPLOYMENT_GUIDE.md` - Complete guide
- `DOCKER_QUICK_START.txt` - Quick reference

Everything is ready for deployment!
