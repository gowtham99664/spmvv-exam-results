#!/bin/bash

set -e

echo "========================================="
echo "Installing Docker and Docker Compose"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root or with sudo"
    exit 1
fi

# Update system
echo "1. Updating system packages..."
yum update -y

# Install required packages
echo ""
echo "2. Installing required packages..."
yum install -y yum-utils device-mapper-persistent-data lvm2

# Add Docker repository
echo ""
echo "3. Adding Docker repository..."
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker
echo ""
echo "4. Installing Docker..."
yum install -y docker-ce docker-ce-cli containerd.io

# Start Docker
echo ""
echo "5. Starting Docker service..."
systemctl start docker
systemctl enable docker

# Install Docker Compose
echo ""
echo "6. Installing Docker Compose..."
DOCKER_COMPOSE_VERSION="2.24.0"
curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Verify installation
echo ""
echo "7. Verifying installation..."
docker --version
docker-compose --version

echo ""
echo "========================================="
echo "✓ Docker and Docker Compose installed successfully!"
echo "========================================="
echo ""
echo "You can now run: ./deploy.sh"
