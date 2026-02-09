# SPMVV Exam Results Management System

A secure, role-based exam results management system built with Django (backend) and React (frontend), deployed with Docker.

## Features

### Admin Features
- Secure login with account lockout after failed attempts
- Upload results via Excel files with comprehensive validation
- View all student results with search functionality
- Change password with strong password policy
- Audit logs for all sensitive operations

### Student Features
- Secure registration with roll number
- View semester-wise results
- Dashboard notifications for new results
- Change password functionality
- Mobile-responsive interface

### Security Features
- JWT-based authentication
- Argon2 password hashing
- Account lockout after 5 failed login attempts
- CSRF and XSS protection
- Audit logging for all operations
- Secure session management
- HTTPS-ready (disable SSL redirect in .env for development)

## Technical Stack

- **Frontend**: React 18, TailwindCSS, Axios, React Router
- **Backend**: Django 5.0, Django REST Framework, SimpleJWT
- **Database**: MySQL 8.0
- **Deployment**: Docker & Docker Compose
- **Server**: Nginx (frontend), Gunicorn (backend)

## Deployment

### Prerequisites
- Docker and Docker Compose installed
- SSH access to server (10.127.248.83)
- Port 2026 available

### Quick Start

```bash
cd ~/spmvv-exam-results
./deploy.sh
```

### Access the Application
- URL: http://10.127.248.83:2026
- Admin Username: admin
- Admin Password: SpmvvExamResults

**IMPORTANT**: Change the admin password immediately after first login!

## Configuration

### Environment Variables (.env)
Key configuration options:
- `SECRET_KEY`: Django secret key (change in production!)
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_*`: Database credentials
- `ADMIN_USERNAME`: Default admin username
- `ADMIN_DEFAULT_PASSWORD`: Default admin password

## Excel Upload Format

Results must be uploaded in the following format:

| Roll Number | Student Name | Semester | Result Type | Subject 1 Code | Subject 1 Name | Subject 1 Internal | Subject 1 External | Subject 1 Total | Subject 1 Result | Subject 1 Grade | ... | Overall Result | Overall Grade |
|-------------|--------------|----------|-------------|----------------|----------------|-------------------|-------------------|----------------|-----------------|----------------|-----|---------------|--------------|

### Required Columns
- Roll Number
- Student Name
- Semester (numeric)
- Result Type (Regular, Supplementary, or Both)

### Subject Columns (repeat for each subject)
- Subject N Code
- Subject N Name
- Subject N Internal (optional)
- Subject N External (optional)
- Subject N Total (optional)
- Subject N Result (Pass, Fail, or Absent)
- Subject N Grade (optional)

### Optional Columns
- Overall Result
- Overall Grade

## Database Backup

### Manual Backup
```bash
cd ~/spmvv-exam-results
./backup.sh
```

### Automated Backups
Add to crontab for daily backups at 2 AM:
```bash
crontab -e
# Add: 0 2 * * * ~/spmvv-exam-results/backup.sh
```

### Restore from Backup
```bash
cd ~/spmvv-exam-results/backups
gunzip spmvv_backup_YYYYMMDD_HHMMSS.sql.gz
docker-compose exec -T db mysql -u root -p${MYSQL_ROOT_PASSWORD} ${DB_NAME} < spmvv_backup_YYYYMMDD_HHMMSS.sql
```

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
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

### Access Django Shell
```bash
docker-compose exec backend python manage.py shell
```

### Run Migrations
```bash
docker-compose exec backend python manage.py migrate
```

### Create Superuser
```bash
docker-compose exec backend python manage.py createsuperuser
```

## Security Best Practices

1. **Change Default Password**: Immediately change the admin password after deployment
2. **Update SECRET_KEY**: Generate a new SECRET_KEY for production
3. **Enable HTTPS**: Set SECURE_SSL_REDIRECT=True after configuring SSL
4. **Regular Backups**: Set up automated daily backups
5. **Monitor Logs**: Regularly check security.log for suspicious activity
6. **Update Dependencies**: Keep all packages up-to-date
7. **Restrict Database Access**: Ensure MySQL is not exposed publicly

## Troubleshooting

### Backend Not Starting
```bash
docker-compose logs backend
docker-compose restart backend
```

### Database Connection Issues
```bash
docker-compose logs db
# Check if database is healthy
docker-compose ps
```

### Frontend Build Errors
```bash
cd frontend
npm install
npm run build
docker-compose build --no-cache frontend
```

### Port Already in Use
```bash
# Check what's using port 2026
sudo lsof -i :2026
# Kill the process or change the port in docker-compose.yml
```

## File Structure

```
spmvv-exam-results/
├── backend/
│   ├── exam_results/         # Django project settings
│   ├── results/              # Main application
│   ├── Dockerfile
│   ├── requirements.txt
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── context/
│   │   └── utils/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── backups/                  # Database backups
├── docker-compose.yml
├── .env
├── deploy.sh
├── backup.sh
└── README.md
```

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review the security logs: `backend/logs/security.log`
3. Check the audit logs in Django admin

## License

Proprietary - SPMVV University
