# SPMVV Quick Reference

## One-Command Deployment
```bash
cd /root/spmvv-exam-results && ./deploy_simple.sh
```

## Check Status
```bash
docker ps
```

## View Logs (Live)
```bash
docker logs -f spmvv_backend     # Backend
docker logs -f spmvv_frontend    # Frontend  
docker logs -f spmvv_db          # Database
```

## Restart Services
```bash
# Restart backend only
docker restart spmvv_backend

# Restart all services
docker restart spmvv_db spmvv_backend spmvv_frontend
```

## Access Application
- **URL:** http://10.127.248.83:2026
- **User:** admin
- **Pass:** SpmvvExamResults

## Common Issues

### Backend won't start?
```bash
docker logs spmvv_backend
docker restart spmvv_db && sleep 10 && docker restart spmvv_backend
```

### Port already in use?
```bash
# Stop host services
systemctl stop mariadb
pkill -f "manage.py runserver"
pkill -f "vite"
```

### Need to redeploy?
```bash
./deploy_simple.sh    # Quick redeploy (5-10 min)
./deploy_docker.sh    # Full redeploy with backup (10-15 min)
```

## File Locations
- **Project:** /root/spmvv-exam-results/
- **Backups:** /root/spmvv-exam-results/backups/
- **Scripts:** 
  - Simple: ./deploy_simple.sh
  - Full: ./deploy_docker.sh

## Deployment Time
- **First build:** 8-10 minutes
- **Rebuild (cached):** 3-5 minutes
- **Container restart:** 30 seconds
