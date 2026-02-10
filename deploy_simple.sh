#!/bin/bash
set -e

echo "=== SPMVV Deployment Script ==="
echo ""

# Config
PROJECT_DIR="/root/spmvv-exam-results"
SERVER_IP=$(hostname -I | awk '{print $1}')

# Database credentials
DB_NAME="spmvv_results"
DB_USER="spmvv_user"
DB_PASSWORD="SpmvvDb@2026"
MYSQL_ROOT_PASSWORD="RootPassword@2026"

# Admin credentials
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="SpmvvExamResults"

echo "[1/5] Stopping old containers..."
docker stop spmvv_backend spmvv_frontend spmvv_db 2>/dev/null || true
docker rm -f spmvv_backend spmvv_frontend spmvv_db 2>/dev/null || true

echo "[2/5] Creating network..."
docker network create spmvv_network 2>/dev/null || true

echo "[3/5] Starting database..."
docker run -d \
  --name spmvv_db \
  --network spmvv_network \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
  -e MYSQL_DATABASE="$DB_NAME" \
  -e MYSQL_USER="$DB_USER" \
  -e MYSQL_PASSWORD="$DB_PASSWORD" \
  -v spmvv_mysql_data:/var/lib/mysql \
  mariadb:10.11

echo "Waiting for database (20s)..."
sleep 20

echo "[4/5] Building and starting backend..."
cd "$PROJECT_DIR/backend"
docker build -t spmvv-backend . >/dev/null 2>&1

docker run -d \
  --name spmvv_backend \
  --network spmvv_network \
  -p 8000:8000 \
  -e SECRET_KEY="django-insecure-docker-$(date +%s)" \
  -e DEBUG=True \
  -e ALLOWED_HOSTS="localhost,127.0.0.1,$SERVER_IP" \
  -e DB_ENGINE=django.db.backends.mysql \
  -e DB_NAME="$DB_NAME" \
  -e DB_USER="$DB_USER" \
  -e DB_PASSWORD="$DB_PASSWORD" \
  -e DB_HOST=spmvv_db \
  -e DB_PORT=3306 \
  -e ADMIN_USERNAME="$ADMIN_USERNAME" \
  -e ADMIN_DEFAULT_PASSWORD="$ADMIN_PASSWORD" \
  -e CORS_ALLOWED_ORIGINS="http://localhost:2026,http://$SERVER_IP:2026" \
  spmvv-backend:latest

echo "Waiting for backend (15s)..."
sleep 15

echo "[5/5] Building and starting frontend..."
cd "$PROJECT_DIR/frontend"
docker build --build-arg VITE_API_URL="http://$SERVER_IP:8000/api" -t spmvv-frontend . >/dev/null 2>&1

docker run -d \
  --name spmvv_frontend \
  --network spmvv_network \
  -p 2026:2026 \
  -e VITE_API_URL="http://$SERVER_IP:8000/api" \
  spmvv-frontend:latest

echo ""
echo "=== Deployment Complete ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Frontend: http://$SERVER_IP:2026"
echo "Backend:  http://$SERVER_IP:8000/api"
echo "Login:    $ADMIN_USERNAME / $ADMIN_PASSWORD"
