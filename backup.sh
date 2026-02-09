#!/bin/bash

set -e

BACKUP_DIR=~/spmvv-exam-results/backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="spmvv_backup_${TIMESTAMP}.sql"

echo "========================================="
echo "SPMVV Exam Results - Database Backup"
echo "========================================="
echo ""

# Create backups directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

echo "Creating database backup..."

# Get database credentials from .env
source ~/spmvv-exam-results/.env

# Create backup using docker-compose
docker-compose exec -T db mysqldump \
    -u root \
    -p${MYSQL_ROOT_PASSWORD} \
    ${DB_NAME} > ${BACKUP_DIR}/${BACKUP_FILE}

# Compress the backup
gzip ${BACKUP_DIR}/${BACKUP_FILE}

echo "Backup created: ${BACKUP_DIR}/${BACKUP_FILE}.gz"
echo ""

# Keep only last 7 backups
echo "Cleaning old backups (keeping last 7)..."
cd ${BACKUP_DIR}
ls -t spmvv_backup_*.sql.gz | tail -n +8 | xargs -r rm

echo ""
echo "Backup complete!"
echo "========================================="
