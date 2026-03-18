#!/bin/bash
# PwnBox-style Attack Environment Setup
# This creates a web-based terminal that users can access
# Just like HackTheBox's PwnBox

set -e

echo "=========================================="
echo "Setting Up PwnBox Attack Environment"
echo "=========================================="

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo bash scripts/install_pwnbox.sh"
    exit 1
fi

# Install Docker and required packages
echo "[1/4] Installing dependencies..."
apt update
apt install -y docker.io docker-compose git

# Create PwnBox Docker Compose file
echo "[2/4] Creating PwnBox configuration..."

mkdir -p /opt/pwnbox
cd /opt/pwnbox

cat > docker-compose.yml <<'EOF'
version: '3.8'

services:
  # Web-based terminal (webshell + xterm.js)
  terminal:
    image: tsl0922/ttyd:latest
    container_name: pwnbox_terminal
    ports:
      - "7681:7681"
    volumes:
      - ./shared:/shared
    environment:
      - PORT=7681
    command: share /bin/bash
    networks:
      - pwnbox_network
    restart: unless-stopped

  # Web-based VNC Desktop (optional - heavier)
  desktop:
    image: dorowu/ubuntu-desktop-lxde-vnc:latest
    container_name: pwnbox_desktop
    ports:
      - "6080:6080"
      - "5900:5900"
    environment:
      - VNC_PASSWORD=cyber training
    volumes:
      - ./shared:/workspace
    networks:
      - pwnbox_network
    restart: unless-stopped

networks:
  pwnbox_network:
    driver: bridge
    ipam:
      config:
        - subnet: 10.100.0.0/24
EOF

cat > .env <<EOF
# PwnBox Configuration
# User VPN network - users connect here
USER_VPN_NETWORK=10.8.0.0/24

# Lab network where machines run
LAB_NETWORK=10.10.10.0/24

# PwnBox internal network
PWNBOX_NETWORK=10.100.0.0/24
EOF

# Create shared directory
mkdir -p shared

# Setup iptables routing
echo "[3/4] Setting up networking..."
# Allow traffic between networks
iptables -A FORWARD -i pwnbox_network -o lab_network -j ACCEPT 2>/dev/null || true
iptables -A FORWARD -i lab_network -o pwnbox_network -j ACCEPT  || true
ipt2>/dev/nullables -A FORWARD -i pwnbox_network -o vpn_network -j ACCEPT 2>/dev/null || true
iptables -A FORWARD -i vpn_network -o pwnbox_network -j ACCEPT 2>/dev/null || true

# Start PwnBox
echo "[4/4] Starting PwnBox services..."
docker-compose up -d

echo ""
echo "=========================================="
echo "PwnBox Setup Complete!"
echo "=========================================="
echo ""
echo "Services:"
echo "- Web Terminal: http://your-server-ip:7681"
echo "- Web Desktop:  http://your-server-ip:6080"
echo ""
echo "These connect to the lab network (10.10.10.0/24)"
echo "Users can access machines directly from the browser!"
echo ""
