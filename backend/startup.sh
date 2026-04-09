#!/bin/sh
# startup.sh - Backend container entrypoint
# Drops stale permission columns (if they exist) before running Django migrations.
# This ensures a clean schema regardless of database volume state.

set -e

echo "=== SPMVV Backend Startup ==="

echo "[1/4] Waiting for database to be ready..."
# Wait up to 60 seconds for the database
for i in $(seq 1 30); do
    python -c "
import MySQLdb, os, sys
try:
    MySQLdb.connect(
        host=os.environ.get('DB_HOST', 'spmvv_db'),
        port=int(os.environ.get('DB_PORT', 3306)),
        user=os.environ.get('DB_USER', 'spmvv_user'),
        passwd=os.environ.get('DB_PASSWORD', ''),
        db=os.environ.get('DB_NAME', 'spmvv_results'),
    )
    sys.exit(0)
except Exception:
    sys.exit(1)
" && break
    echo "  Database not ready, retrying in 2s... ($i/30)"
    sleep 2
done

echo "[2/4] Cleaning stale columns from database (if any)..."
python -c "
import MySQLdb, os
conn = MySQLdb.connect(
    host=os.environ.get('DB_HOST', 'spmvv_db'),
    port=int(os.environ.get('DB_PORT', 3306)),
    user=os.environ.get('DB_USER', 'spmvv_user'),
    passwd=os.environ.get('DB_PASSWORD', ''),
    db=os.environ.get('DB_NAME', 'spmvv_results'),
)
cursor = conn.cursor()

# Check if results_user table exists
cursor.execute(\"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'results_user'\")
if cursor.fetchone()[0] == 0:
    print('  Table results_user does not exist yet. Skipping.')
else:
    cursor.execute(
        \"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS \"
        \"WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'results_user'\"
    )
    existing = {row[0] for row in cursor.fetchall()}
    stale = ['can_manage_users', 'can_view_all_branches', 'can_upload_results', 'can_delete_results', 'can_view_statistics']
    for col in stale:
        if col in existing:
            print(f'  Dropping stale column: {col}')
            cursor.execute(f'ALTER TABLE results_user DROP COLUMN {col}')
            conn.commit()
    print('  Stale column cleanup done.')

conn.close()
"

echo "[3/4] Running Django migrations..."
python manage.py migrate

echo "[4/4] Initializing admin user..."
python manage.py init_admin --force

echo "=== Starting Gunicorn ==="
exec gunicorn exam_results.wsgi:application --bind 0.0.0.0:8000 --workers 4
