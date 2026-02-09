#!/bin/bash
set -e

# Load environment variables
source .env

# Create network
podman network exists spmvv_network 2>/dev/null || podman network create spmvv_network

# Start MySQL
echo "Starting MySQL..."
podman run -d \
  --name spmvv_db \
  --network spmvv_network \
  -e MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} \
  -e MYSQL_DATABASE=${DB_NAME} \
  -e MYSQL_USER=${DB_USER} \
  -e MYSQL_PASSWORD=${DB_PASSWORD} \
  -p 3306:3306 \
  -v spmvv_mysql_data:/var/lib/mysql \
  --restart=always \
  docker.io/library/mysql:8.0

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
sleep 30

# Start Backend
echo "Starting Backend..."
podman run -d \
  --name spmvv_backend \
  --network spmvv_network \
  -e SECRET_KEY="${SECRET_KEY}" \
  -e DEBUG="${DEBUG}" \
  -e ALLOWED_HOSTS="${ALLOWED_HOSTS}" \
  -e DB_ENGINE="${DB_ENGINE}" \
  -e DB_NAME="${DB_NAME}" \
  -e DB_USER="${DB_USER}" \
  -e DB_PASSWORD="${DB_PASSWORD}" \
  -e DB_HOST=spmvv_db \
  -e DB_PORT=3306 \
  -e JWT_ACCESS_TOKEN_LIFETIME="${JWT_ACCESS_TOKEN_LIFETIME}" \
  -e JWT_REFRESH_TOKEN_LIFETIME="${JWT_REFRESH_TOKEN_LIFETIME}" \
  -e ADMIN_USERNAME="${ADMIN_USERNAME}" \
  -e ADMIN_DEFAULT_PASSWORD="${ADMIN_DEFAULT_PASSWORD}" \
  -p 8000:8000 \
  -v $PWD/backend:/app \
  --restart=always \
  localhost/spmvv-backend:latest

echo "Application starting..."
echo "Backend logs:"
sleep 5
podman logs spmvv_backend

echo ""
echo "Check status with: podman ps"
echo "View logs with: podman logs -f spmvv_backend"
