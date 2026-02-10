#!/bin/bash
set -e

PROJECT_DIR="/root/spmvv-exam-results"
SERVER_IP=$(hostname -I | awk '{print $1}')

# Credentials
DB_NAME="spmvv_results"
DB_USER="spmvv_user"
DB_PASSWORD="SpmvvDb@2026"
MYSQL_ROOT_PASSWORD="RootPassword@2026"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="SpmvvExamResults"

echo "=== SPMVV Deployment ==="
echo ""

# Cleanup
echo "[1/5] Cleanup..."
docker stop spmvv_backend spmvv_frontend spmvv_db 2>/dev/null || true
docker rm -f spmvv_backend spmvv_frontend spmvv_db 2>/dev/null || true
pkill -9 -f "npm" 2>/dev/null || true
sleep 2

# Network
echo "[2/5] Network..."
docker network create spmvv_network 2>/dev/null || true

# Database
echo "[3/5] Database..."
docker run -d --name spmvv_db --network spmvv_network -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD="$MYSQL_ROOT_PASSWORD" \
  -e MYSQL_DATABASE="$DB_NAME" \
  -e MYSQL_USER="$DB_USER" \
  -e MYSQL_PASSWORD="$DB_PASSWORD" \
  -v spmvv_mysql_data:/var/lib/mysql \
  mariadb:10.11
echo "  Waiting 20s..."
sleep 20

# Backend
echo "[4/5] Backend..."
cd "$PROJECT_DIR/backend"
docker build -q -t spmvv-backend . 2>/dev/null || docker build -t spmvv-backend .
docker run -d --name spmvv_backend --network spmvv_network -p 8000:8000 \
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
sleep 10

# Frontend
echo "[5/5] Frontend..."
cd "$PROJECT_DIR/frontend"
pkill -9 -f "docker.*build" 2>/dev/null || true
sleep 2

# Try build with 10 min timeout
echo "  Building (may take 5-10 min on slow VMs)..."
if ! timeout 600 docker build -q --build-arg VITE_API_URL="http://$SERVER_IP:8000/api" -t spmvv-frontend . 2>/dev/null; then
  echo "  First attempt failed, retrying..."
  docker build --no-cache --build-arg VITE_API_URL="http://$SERVER_IP:8000/api" -t spmvv-frontend .
fi

docker run -d --name spmvv_frontend --network spmvv_network -p 2026:2026 \
  -e VITE_API_URL="http://$SERVER_IP:8000/api" \
  spmvv-frontend:latest
sleep 5

echo ""
echo "=== DONE ==="
docker ps --format "{{.Names}}: {{.Status}}"
echo ""
echo "Frontend: http://$SERVER_IP:2026"
echo "Login: $ADMIN_USERNAME / $ADMIN_PASSWORD"
