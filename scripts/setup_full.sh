#!/bin/bash
# Complete Setup Script for Cyber Training Platform
# This sets up everything needed for VPN-based lab access

set -e

echo "=========================================="
echo "Cyber Training Platform - Full Setup"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo bash setup_full.sh"
    exit 1
fi

echo ""
echo "This script will:"
echo "1. Install Docker and Docker Compose"
echo "2. Set up OpenVPN server"
echo "3. Configure lab network"
echo "4. Start the platform"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Step 1: Install Docker
echo "[1/5] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    usermod -aG docker $USER
fi

if ! command -v docker-compose &> /dev/null; then
    apt install -y docker-compose
fi

# Step 2: Install OpenVPN
echo "[2/5] Installing OpenVPN..."
apt update
apt install -y openvpn easy-rsa iptables-persistent

# Step 3: Setup OpenVPN Server
echo "[3/5] Setting up OpenVPN server..."
bash scripts/setup_openvpn.sh

# Step 4: Create lab network
echo "[4/5] Creating lab Docker network..."
docker network create lab_network 2>/dev/null || echo "Lab network already exists"
docker network create vpn_network 2>/dev/null || echo "VPN network already exists"

# Step 5: Build and start containers
echo "[5/5] Starting platform..."
cd "$(dirname "$0")"

# Get server IP
SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
echo "Your server IP is: $SERVER_IP"
echo "Users should connect to: $SERVER_IP:1194"

# Create environment file
cat > .env <<EOF
VPN_SERVER_IP=$SERVER_IP
OVPN_PORT=1194
OVPN_PROTO=udp
EOF

# Start the platform
docker-compose -f docker-compose.full.yml up -d --build

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Platform URLs:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo ""
echo "VPN Connection Info:"
echo "- Server: $SERVER_IP"
echo "- Port: 1194 (UDP)"
echo "- Protocol: UDP"
echo ""
echo "Next steps:"
echo "1. Register a user at http://localhost:3000/register"
echo "2. Create VPN config: sudo bash scripts/create_client.sh <username>"
echo "3. Download config from /etc/openvpn/client-configs/"
echo "4. Connect using OpenVPN client"
echo ""
echo "To create more users:"
echo "  sudo bash scripts/create_client.sh <username>"
echo ""
