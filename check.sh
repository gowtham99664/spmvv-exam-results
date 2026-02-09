#!/bin/bash

echo "========================================="
echo "SPMVV Exam Results - Pre-Deployment Check"
echo "========================================="
echo ""

ERRORS=0

# Check Docker
echo "1. Checking Docker..."
if command -v docker &> /dev/null; then
    echo "   ✓ Docker is installed"
    docker --version
else
    echo "   ✗ Docker is not installed"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check Docker Compose
echo "2. Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    echo "   ✓ Docker Compose is installed"
    docker-compose --version
else
    echo "   ✗ Docker Compose is not installed"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check project directory
echo "3. Checking project structure..."
if [ -d ~/spmvv-exam-results/backend ] && [ -d ~/spmvv-exam-results/frontend ]; then
    echo "   ✓ Project directories exist"
else
    echo "   ✗ Project directories missing"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check .env file
echo "4. Checking configuration..."
if [ -f ~/spmvv-exam-results/.env ]; then
    echo "   ✓ .env file exists"
else
    echo "   ✗ .env file missing"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check backend files
echo "5. Checking backend files..."
BACKEND_FILES=(
    "backend/requirements.txt"
    "backend/manage.py"
    "backend/Dockerfile"
    "backend/exam_results/settings.py"
    "backend/results/models.py"
    "backend/results/views.py"
    "backend/results/urls.py"
)

for file in "${BACKEND_FILES[@]}"; do
    if [ -f ~/spmvv-exam-results/$file ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file missing"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# Check frontend files
echo "6. Checking frontend files..."
FRONTEND_FILES=(
    "frontend/package.json"
    "frontend/Dockerfile"
    "frontend/nginx.conf"
    "frontend/src/App.jsx"
    "frontend/src/main.jsx"
)

for file in "${FRONTEND_FILES[@]}"; do
    if [ -f ~/spmvv-exam-results/$file ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file missing"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# Check port availability
echo "7. Checking port availability..."
if ! lsof -i :2026 &> /dev/null; then
    echo "   ✓ Port 2026 is available"
else
    echo "   ⚠ Port 2026 is in use"
    lsof -i :2026
fi
echo ""

# Summary
echo "========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✓ All checks passed! Ready to deploy."
    echo ""
    echo "Run: ./deploy.sh"
else
    echo "✗ $ERRORS error(s) found. Please fix before deploying."
fi
echo "========================================="
