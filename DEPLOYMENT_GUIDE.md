# SPMVV Exam Results - Complete Deployment Guide

## Server Information
- **IP Address**: 10.127.248.83
- **Port**: 2026
- **SSH Access**: Passwordless SSH configured

## Quick Start (If Docker is Already Installed)

```bash
cd ~/spmvv-exam-results
./check.sh           # Run pre-deployment check
./deploy.sh          # Deploy the application
```

Access at: http://10.127.248.83:2026

## Full Installation (Fresh Server)

### Step 1: Install Docker and Docker Compose

```bash
cd ~/spmvv-exam-results
sudo ./install-docker.sh
```

This will:
- Update system packages
- Install Docker CE
- Install Docker Compose
- Start and enable Docker service
- Verify installation

### Step 2: Verify Installation

```bash
./check.sh
```

You should see all checks passed.

### Step 3: Review Configuration

```bash
cat .env
```

**Important Settings to Review:**
- `SECRET_KEY`: Should be unique and kept secret
- `DB_PASSWORD`: Database password
- `MYSQL_ROOT_PASSWORD`: MySQL root password
- `ADMIN_DEFAULT_PASSWORD`: Change after first login

### Step 4: Deploy Application

```bash
./deploy.sh
```

This will:
1. Stop any existing containers
2. Build Docker images (takes 5-10 minutes first time)
3. Start all services (database, backend, frontend)
4. Run database migrations
5. Create default admin user
6. Wait for health checks

### Step 5: Verify Deployment

```bash
# Check container status
docker-compose ps

# Check logs
docker-compose logs -f

# Test backend health
curl http://10.127.248.83:8000/api/health/

# Test frontend
curl http://10.127.248.83:2026/
```

### Step 6: Access Application

Open browser and navigate to:
```
http://10.127.248.83:2026
```

**Default Admin Credentials:**
- Username: `admin`
- Password: `SpmvvExamResults`

**IMPORTANT**: Change the admin password immediately after first login!

## Post-Deployment Tasks

### 1. Change Admin Password
1. Login as admin
2. Go to Settings or Profile
3. Click "Change Password"
4. Enter old password: `SpmvvExamResults`
5. Enter and confirm new strong password

### 2. Setup Automated Backups

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * ~/spmvv-exam-results/backup.sh
```

### 3. Test Student Registration
1. Click "Register" on login page
2. Create a test student account
3. Login and verify access

### 4. Test Result Upload
1. Login as admin
2. Prepare Excel file (see EXCEL_TEMPLATE_GUIDE.md)
3. Upload test results
4. Verify student can see results

## Management Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Stop Application
```bash
docker-compose down
```

### Start Application
```bash
docker-compose up -d
```

### Database Backup
```bash
./backup.sh
```

Backups are stored in: `~/spmvv-exam-results/backups/`

### Database Restore
```bash
cd ~/spmvv-exam-results/backups
gunzip spmvv_backup_YYYYMMDD_HHMMSS.sql.gz
docker-compose exec -T db mysql -u root -p${MYSQL_ROOT_PASSWORD} spmvv_results < spmvv_backup_YYYYMMDD_HHMMSS.sql
```

### View Database
```bash
# Access MySQL
docker-compose exec db mysql -u root -p${MYSQL_ROOT_PASSWORD} spmvv_results

# Common queries
USE spmvv_results;
SHOW TABLES;
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM results;
```

### Django Admin Panel
Access at: http://10.127.248.83:8000/admin/

Use admin credentials to login.

### Django Shell
```bash
docker-compose exec backend python manage.py shell
```

### Create Additional Admin Users
```bash
docker-compose exec backend python manage.py createsuperuser
```

## Troubleshooting

### Issue: Containers won't start
```bash
# Check logs
docker-compose logs

# Check Docker status
systemctl status docker

# Restart Docker
sudo systemctl restart docker
```

### Issue: Database connection errors
```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Issue: Frontend not loading
```bash
# Check nginx logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Issue: Backend API errors
```bash
# Check backend logs
docker-compose logs backend

# Check migrations
docker-compose exec backend python manage.py showmigrations

# Apply migrations
docker-compose exec backend python manage.py migrate
```

### Issue: Port already in use
```bash
# Find what's using port 2026
sudo lsof -i :2026

# Kill the process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

### Issue: Out of disk space
```bash
# Clean Docker system
docker system prune -a

# Remove old images
docker image prune -a

# Check disk usage
df -h
docker system df
```

## Security Checklist

- [ ] Changed default admin password
- [ ] Updated SECRET_KEY in .env
- [ ] Updated database passwords
- [ ] Verified HTTPS is enabled (if SSL configured)
- [ ] Set up automated backups
- [ ] Reviewed security logs
- [ ] Tested account lockout after failed logins
- [ ] Verified students can only see their own results
- [ ] Tested Excel upload validation
- [ ] Configured firewall rules

## Monitoring

### Check System Health
```bash
# Application health
curl http://10.127.248.83:8000/api/health/

# Container status
docker-compose ps

# Container resource usage
docker stats
```

### Review Logs
```bash
# Security log
docker-compose exec backend cat logs/security.log

# Application log
docker-compose exec backend cat logs/app.log
```

### Database Status
```bash
docker-compose exec db mysqladmin -u root -p${MYSQL_ROOT_PASSWORD} status
```

## Updating the Application

### Update Code
```bash
# Pull latest changes (if using git)
cd ~/spmvv-exam-results
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Update Dependencies
```bash
# Backend
cd backend
# Update requirements.txt
docker-compose build --no-cache backend

# Frontend
cd frontend
# Update package.json
docker-compose build --no-cache frontend
```

## Rollback

### Rollback Application
```bash
# Stop current version
docker-compose down

# Restore code from backup
# (maintain backups of working versions)

# Rebuild
docker-compose build
docker-compose up -d
```

### Rollback Database
```bash
# Restore from backup
cd ~/spmvv-exam-results/backups
gunzip spmvv_backup_YYYYMMDD_HHMMSS.sql.gz
docker-compose exec -T db mysql -u root -p${MYSQL_ROOT_PASSWORD} spmvv_results < spmvv_backup_YYYYMMDD_HHMMSS.sql
```

## Support Information

### Log Locations
- Application logs: `backend/logs/app.log`
- Security logs: `backend/logs/security.log`
- Docker logs: `docker-compose logs`

### Configuration Files
- Main config: `.env`
- Django settings: `backend/exam_results/settings.py`
- Docker config: `docker-compose.yml`

### Important Directories
- Backups: `~/spmvv-exam-results/backups/`
- Database: Docker volume `mysql_data`
- Static files: Docker volume `static_volume`
- Media files: Docker volume `media_volume`

## Contact

For technical issues or questions about deployment, contact the system administrator.
