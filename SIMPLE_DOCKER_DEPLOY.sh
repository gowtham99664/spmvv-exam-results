#!/bin/bash

# Simple Docker/Podman Deployment - Step by Step

set -e

echo "=========================================="
echo "SPMVV - Simple Docker Deployment"
echo "=========================================="
echo ""

cd /root/spmvv-exam-results

# Step 1: Stop old containers
echo "[1/8] Stopping old containers..."
podman stop spmvv_backend spmvv_frontend spmvv_db 2>/dev/null || true
podman rm spmvv_backend spmvv_frontend spmvv_db 2>/dev/null || true
echo "✓ Done"
echo ""

# Step 2: Create network
echo "[2/8] Creating network..."
podman network create spmvv_network 2>/dev/null || echo "Network already exists"
echo "✓ Done"
echo ""

# Step 3: Start database
echo "[3/8] Starting MariaDB database..."
podman run -d \
  --name spmvv_db \
  --network spmvv_network \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=RootPassword@2026 \
  -e MYSQL_DATABASE=spmvv_results \
  -e MYSQL_USER=spmvv_user \
  -e MYSQL_PASSWORD=SpmvvDb@2026 \
  -v spmvv_mysql_data:/var/lib/mysql \
  mariadb:10.11

echo "Waiting for database to be ready (20 seconds)..."
sleep 20
echo "✓ Database started"
echo ""

# Step 4: Build backend
echo "[4/8] Building backend image..."
cd backend
podman build -t spmvv_backend:latest . 
cd ..
echo "✓ Backend image built"
echo ""

# Step 5: Start backend
echo "[5/8] Starting backend..."
podman run -d \
  --name spmvv_backend \
  --network spmvv_network \
  -p 8000:8000 \
  -e SECRET_KEY=django-insecure-docker-change-in-production \
  -e DEBUG=True \
  -e ALLOWED_HOSTS=localhost,127.0.0.1,10.127.248.83,backend \
  -e DB_ENGINE=django.db.backends.mysql \
  -e DB_NAME=spmvv_results \
  -e DB_USER=spmvv_user \
  -e DB_PASSWORD=SpmvvDb@2026 \
  -e DB_HOST=spmvv_db \
  -e DB_PORT=3306 \
  -e ADMIN_USERNAME=admin \
  -e ADMIN_DEFAULT_PASSWORD=SpmvvExamResults \
  -e CORS_ALLOWED_ORIGINS=http://localhost:2026,http://127.0.0.1:2026,http://10.127.248.83:2026 \
  spmvv_backend:latest

echo "Waiting for backend to initialize (15 seconds)..."
sleep 15
echo "✓ Backend started"
echo ""

# Step 6: Build frontend
echo "[6/8] Building frontend image..."
cd frontend
podman build -t spmvv_frontend:latest --build-arg VITE_API_URL=http://10.127.248.83:8000/api .
cd ..
echo "✓ Frontend image built"
echo ""

# Step 7: Start frontend
echo "[7/8] Starting frontend..."
podman run -d \
  --name spmvv_frontend \
  --network spmvv_network \
  -p 2026:2026 \
  -e VITE_API_URL=http://10.127.248.83:8000/api \
  spmvv_frontend:latest

echo "✓ Frontend started"
echo ""

# Step 8: Configure firewall
echo "[8/8] Configuring firewall..."
if systemctl is-active --quiet firewalld; then
    firewall-cmd --permanent --add-port=8000/tcp 2>/dev/null || true
    firewall-cmd --permanent --add-port=2026/tcp 2>/dev/null || true
    firewall-cmd --reload 2>/dev/null || true
    echo "✓ Firewall configured"
else
    echo "⚠ Firewall not running"
fi
echo ""

echo "=========================================="
echo "✓ Deployment Complete!"
echo "=========================================="
echo ""
echo "Access URLs:"
echo "  Frontend: http://10.127.248.83:2026"
echo "  Backend:  http://10.127.248.83:8000/api"
echo ""
echo "Login:"
echo "  Username: admin"
echo "  Password: SpmvvExamResults"
echo ""
echo "Check status:"
echo "  podman ps"
echo ""
echo "View logs:"
echo "  podman logs spmvv_backend"
echo "  podman logs spmvv_frontend"
echo ""
