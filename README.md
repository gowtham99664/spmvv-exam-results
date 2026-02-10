# SPMVV Exam Results - Docker Deployment

Django REST API backend + React frontend for managing student exam results.

## Quick Start

### Deploy
```bash
cd /root/spmvv-exam-results
./deploy_simple.sh
```

### Access
- **URL:** http://10.127.248.83:2026
- **Username:** admin
- **Password:** SpmvvExamResults

---

## Deployment Options

### Option 1: Quick Deploy (Recommended)
```bash
./deploy_simple.sh
```
- **Time:** 5-10 minutes
- **Use for:** Daily deployments, testing, development

### Option 2: Full Deploy (With Backup)
```bash
./deploy_docker.sh
```
- **Time:** 10-15 minutes
- **Includes:** Automatic database backup and restore
- **Use for:** Production deployments, important updates

---

## Common Commands

### Check Status
```bash
docker ps
```

### View Logs
```bash
docker logs -f spmvv_backend
docker logs -f spmvv_frontend
docker logs -f spmvv_db
```

### Restart Services
```bash
# Restart single service
docker restart spmvv_backend

# Restart all services
docker restart spmvv_db spmvv_backend spmvv_frontend
```

### Stop/Start Services
```bash
# Stop all
docker stop spmvv_db spmvv_backend spmvv_frontend

# Start all
docker start spmvv_db && sleep 10 && docker start spmvv_backend spmvv_frontend
```

---

## Architecture

```
Frontend (React + Vite)     → Port 2026
    ↓
Backend (Django + Gunicorn) → Port 8000
    ↓
Database (MariaDB 10.11)    → Port 3306 (internal)
```

**Network:** All containers on `spmvv_network` bridge network  
**Volume:** Database data persisted in `spmvv_mysql_data` volume

---

## Performance

| Action | Time |
|--------|------|
| First deployment | 8-10 min |
| Redeployment (cached) | 3-5 min |
| Container restart | 30 sec |

**Optimizations:**
- Multi-stage Docker build
- Smart layer caching
- Dependencies cached until requirements.txt changes

---

## Troubleshooting

### Backend won't start?
```bash
docker logs spmvv_backend
docker restart spmvv_db && sleep 10 && docker restart spmvv_backend
```

### Frontend not loading?
```bash
docker logs spmvv_frontend
docker restart spmvv_frontend
```

### Database connection issues?
```bash
docker logs spmvv_db
docker restart spmvv_db && sleep 15 && docker restart spmvv_backend
```

### Port conflicts?
```bash
# Stop conflicting services
systemctl stop mariadb
pkill -f "manage.py runserver"
pkill -f "vite"

# Then redeploy
./deploy_simple.sh
```

---

## Project Structure

```
/root/spmvv-exam-results/
├── deploy_simple.sh       # Quick deployment script
├── deploy_docker.sh       # Full deployment with backup
├── README.md              # This file
├── QUICKSTART.md          # Quick reference
├── backend/
│   ├── Dockerfile         # Optimized multi-stage build
│   ├── requirements.txt   # Python dependencies
│   ├── manage.py
│   └── ...
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── ...
└── backups/               # Database backups (auto-generated)
```

---

## Configuration

### Database
- **Name:** spmvv_results
- **User:** spmvv_user
- **Password:** SpmvvDb@2026
- **Root Password:** RootPassword@2026

### Admin User
- **Username:** admin
- **Password:** SpmvvExamResults
- **Created automatically on first deployment**

### Environment Variables
Backend container uses these environment variables:
- `DEBUG=True` (change to False for production)
- `DB_HOST=spmvv_db` (container name)
- `CORS_ALLOWED_ORIGINS` (includes frontend URL)

---

## Backup & Restore

### Manual Backup
```bash
docker exec spmvv_db mysqldump -u spmvv_user -pSpmvvDb@2026 spmvv_results > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Manual Restore
```bash
docker exec -i spmvv_db mysql -u spmvv_user -pSpmvvDb@2026 spmvv_results < backup_file.sql
```

### Automatic Backup
Use `deploy_docker.sh` for automatic backup before redeployment.

**Backups stored in:** `/root/spmvv-exam-results/backups/`

---

## Production Hardening (TODO)

- [ ] Set `DEBUG=False` in backend
- [ ] Generate unique `SECRET_KEY`
- [ ] Change default admin password
- [ ] Add Nginx reverse proxy
- [ ] Set up SSL/TLS certificates
- [ ] Implement rate limiting
- [ ] Add systemd services for auto-start
- [ ] Set up monitoring and alerting
- [ ] Configure automated backups

---

## Technical Details

### Backend (Django)
- **Framework:** Django 5.0.9 + DRF
- **WSGI Server:** Gunicorn (4 workers)
- **Database:** MySQL (via mysqlclient)
- **Auth:** JWT (djangorestframework-simplejwt)
- **Features:** Excel upload (openpyxl), CORS, rate limiting

### Frontend (React)
- **Framework:** React 18 + Vite
- **UI:** Tailwind CSS
- **Routing:** React Router
- **HTTP:** Axios
- **Dev Server:** Vite dev server (port 2026)

### Database (MariaDB)
- **Version:** 10.11
- **Storage Engine:** InnoDB
- **Character Set:** utf8mb4
- **Volume:** Persistent Docker volume

---

## Support

For issues or questions:
1. Check logs: `docker logs -f spmvv_backend`
2. Verify containers: `docker ps`
3. Restart services: `docker restart spmvv_backend`
4. Full redeploy: `./deploy_simple.sh`

---

**Last Updated:** Feb 10, 2026  
**Status:** ✅ Running  
**Deployment:** Docker-based
