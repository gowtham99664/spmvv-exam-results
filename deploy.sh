#!/bin/bash

set -e

echo "========================================="
echo "SPMVV Exam Results - Deployment Script"
echo "========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed"
    exit 1
fi

# Navigate to project directory
cd ~/spmvv-exam-results

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

echo "1. Stopping existing containers..."
docker-compose down

echo ""
echo "2. Building Docker images..."
docker-compose build --no-cache

echo ""
echo "3. Starting services..."
docker-compose up -d

echo ""
echo "4. Waiting for services to be healthy..."
sleep 10

# Check backend health
echo "   Checking backend health..."
for i in {1..30}; do
    if docker-compose exec -T backend curl -f http://localhost:8000/api/health/ 2>/dev/null; then
        echo "   ✓ Backend is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ✗ Backend health check failed"
        docker-compose logs backend
        exit 1
    fi
    sleep 2
done

echo ""
echo "5. Creating backups directory..."
mkdir -p ~/spmvv-exam-results/backups

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Access the application at: http://10.127.248.83:2026"
echo ""
echo "Default Admin Credentials:"
echo "  Username: admin"
echo "  Password: SpmvvExamResults"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart:          docker-compose restart"
echo "  Backup database:  ./backup.sh"
echo ""
