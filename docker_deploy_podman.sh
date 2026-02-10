#!/bin/bash

# SPMVV Exam Results - Podman Deployment Script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "SPMVV Exam Results - Podman Deployment"
echo -e "==========================================${NC}\n"

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
if [ -z "$SERVER_IP" ]; then
    SERVER_IP="localhost"
fi

echo -e "${YELLOW}[1/6] Checking Podman installation...${NC}"

if ! command -v podman &> /dev/null; then
    echo -e "${RED}✗ Podman not found${NC}"
    exit 1
fi

if ! command -v podman-compose &> /dev/null; then
    echo -e "${YELLOW}Installing podman-compose...${NC}"
    pip3 install podman-compose
fi

echo -e "${GREEN}✓ Podman version: $(podman --version)${NC}"
echo -e "${GREEN}✓ Podman-compose available${NC}\n"

echo -e "${YELLOW}[2/6] Creating .env file...${NC}"

cat > .env <<EOF
# Database Configuration
MYSQL_ROOT_PASSWORD=RootPassword@2026
DB_NAME=spmvv_results
DB_USER=spmvv_user
DB_PASSWORD=SpmvvDb@2026

# Django Configuration
SECRET_KEY=django-insecure-docker-$(date +%s)-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,$SERVER_IP,backend

# Admin User - FIXED CREDENTIALS
ADMIN_USERNAME=admin
ADMIN_DEFAULT_PASSWORD=SpmvvExamResults

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# API URL (for frontend)
VITE_API_URL=http://$SERVER_IP:8000/api
EOF

echo -e "${GREEN}✓ .env file created${NC}\n"

echo -e "${YELLOW}[3/6] Stopping existing containers...${NC}"
podman-compose down 2>/dev/null || true
echo -e "${GREEN}✓ Existing containers stopped${NC}\n"

echo -e "${YELLOW}[4/6] Building images (this takes 5-10 minutes)...${NC}"
podman-compose build --no-cache
echo -e "${GREEN}✓ Images built${NC}\n"

echo -e "${YELLOW}[5/6] Starting containers...${NC}"
podman-compose up -d
echo -e "${GREEN}✓ Containers started${NC}\n"

echo -e "${YELLOW}[6/6] Waiting for services (30 seconds)...${NC}"
sleep 30

# Check containers
echo -e "\nChecking container status..."
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Configure firewall
if systemctl is-active --quiet firewalld; then
    echo -e "\n${YELLOW}Configuring firewall...${NC}"
    firewall-cmd --permanent --add-port=8000/tcp 2>/dev/null || true
    firewall-cmd --permanent --add-port=2026/tcp 2>/dev/null || true
    firewall-cmd --reload 2>/dev/null || true
    echo -e "${GREEN}✓ Firewall configured${NC}"
fi

echo -e "\n${GREEN}=========================================="
echo "✓ Deployment completed!"
echo -e "==========================================${NC}\n"

echo -e "${BLUE}Access URLs:${NC}"
echo -e "  Frontend: ${GREEN}http://$SERVER_IP:2026${NC}"
echo -e "  Backend:  ${GREEN}http://$SERVER_IP:8000/api${NC}"
echo ""

echo -e "${BLUE}Default Login Credentials:${NC}"
echo -e "  Username: ${GREEN}admin${NC}"
echo -e "  Password: ${GREEN}SpmvvExamResults${NC}"
echo ""

echo -e "${BLUE}Useful Commands:${NC}"
echo "  View logs:       podman-compose logs -f"
echo "  Backend logs:    podman logs -f spmvv_backend"
echo "  Frontend logs:   podman logs -f spmvv_frontend"
echo "  Stop:            podman-compose down"
echo "  Restart:         podman-compose restart"
echo "  Status:          podman ps"
echo ""

echo -e "${YELLOW}Checking backend health...${NC}"
sleep 5
curl -s http://localhost:8000/api/ | head -20 || echo "Backend starting up..."

echo -e "\n${GREEN}Done! Access the application at http://$SERVER_IP:2026${NC}"
