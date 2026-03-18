#!/bin/bash
# OpenVPN Server Setup Script for Cyber Training Platform
# Run as: sudo bash setup_openvpn.sh

set -e

echo "=========================================="
echo "Cyber Training Platform - OpenVPN Setup"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo bash setup_openvpn.sh"
    exit 1
fi

# Configuration
VPN_SERVER_IP=$(curl -s ifconfig.me || echo "YOUR_SERVER_IP")
VPN_NETWORK="10.8.0.0/24"
VPN_LAB_NETWORK="10.10.10.0/24"
OVPN_PORT=1194
OVPN_PROTO="udp"

echo "Server IP will be: $VPN_SERVER_IP"
echo "VPN Network: $VPN_NETWORK"
echo "Lab Network: $VPN_LAB_NETWORK"

# Update system
echo "[1/6] Updating system..."
apt update && apt upgrade -y

# Install OpenVPN and EasyRSA
echo "[2/6] Installing OpenVPN and dependencies..."
apt install -y openvpn easy-rsa iptables-persistent

# Setup EasyRSA for certificates
echo "[3/6] Setting up PKI..."
mkdir -p /etc/openvpn/easy-rsa
cp -r /usr/share/easy-rsa/* /etc/openvpn/easy-rsa/
cd /etc/openvpn/easy-rsa

# Initialize PKI
./easyrsa init-pki

# Build CA
echo "Building CA certificate (press enter for defaults)..."
./easyrsa build-ca nopass

# Build server certificate
echo "Building server certificate..."
./easyrsa build-server-full server nopass

# Generate Diffie-Hellman parameters
echo "Generating DH parameters (this may take a while)..."
./easyrsa gen-dh

# Generate TLS auth key
openvpn --genkey secret /etc/openvpn/pki/ta.key

# Create OpenVPN server config
echo "[4/6] Creating OpenVPN server configuration..."
cat > /etc/openvpn/server.conf <<EOF
# CyberTraining OpenVPN Server Config
port $OVPN_PORT
proto $OVPN_PROTO
dev tun
ca /etc/openvpn/pki/ca.crt
cert /etc/openvpn/pki/issued/server.crt
key /etc/openvpn/pki/private/server.key
dh /etc/openvpn/pki/dh.pem
tls-auth /etc/openvpn/pki/ta.key 0

# Network configuration
server $VPN_NETWORK 255.255.255.0
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 1.1.1.1"
push "dhcp-option DNS 8.8.8.8"

# Allow access to lab network
push "route $VPN_LAB_NETWORK 255.255.255.0"

# Keep alive
keepalive 10 60

# Security
cipher AES-256-CBC
auth SHA256
comp-lzo
persist-key
persist-tun
status /var/log/openvpn/status.log
verb 3

# Client configuration directory
client-config-dir /etc/openvpn/ccd
EOF

# Create CCD directory for client-specific configs
mkdir -p /etc/openvpn/ccd

# Enable IP forwarding
echo "[5/6] Configuring networking..."
echo 1 > /proc/sys/net/ipv4/ip_forward
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

# Setup iptables rules for NAT
iptables -t nat -A POSTROUTING -s $VPN_NETWORK -o eth0 -j MASQUERADE
iptables -A FORWARD -i tun0 -o eth0 -j ACCEPT
iptables -A FORWARD -i eth0 -o tun0 -j ACCEPT
iptables -A FORWARD -i tun0 -o tun0 -j ACCEPT

# Allow VPN traffic
iptables -A INPUT -p $OVPN_PROTO --dport $OVPN_PORT -j ACCEPT
iptables -A INPUT -i tun+ -j ACCEPT
iptables -A OUTPUT -o tun+ -j ACCEPT

# Save iptables rules
iptables-save > /etc/iptables/rules.v4 2>/dev/null || iptables-save > /etc/iptables.openvpn

# Create client config template
echo "[6/6] Creating client configuration template..."
cat > /etc/openvpn/client-template.conf <<EOF
# CyberTraining Lab VPN Client Config
client
dev tun
proto $OVPN_PROTO
remote $VPN_SERVER_IP $OVPN_PORT
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
auth SHA256
comp-lzo
verb 3

<ca>
# CA Certificate - copy from /etc/openvpn/pki/ca.crt
</ca>

<cert>
# Client Certificate
</cert>

<key>
# Client Key
</key>

<tls-auth>
# TLS Auth Key - copy from /etc/openvpn/pki/ta.key
</tls-auth>
key-direction 1
EOF

# Start and enable OpenVPN
echo "Starting OpenVPN service..."
systemctl enable openvpn@server
systemctl start openvpn@server
systemctl status openvpn@server --no-pager || true

echo ""
echo "=========================================="
echo "OpenVPN Server Setup Complete!"
echo "=========================================="
echo ""
echo "Server IP: $VPN_SERVER_IP"
echo "Port: $OVPN_PORT"
echo "Protocol: $OVPN_PROTO"
echo "VPN Network: $VPN_NETWORK"
echo "Lab Network: $VPN_LAB_NETWORK"
echo ""
echo "Certificate files location: /etc/openvpn/pki/"
echo "- CA cert: /etc/openvpn/pki/ca.crt"
echo "- TA key: /etc/openvpn/pki/ta.key"
echo ""
echo "Next steps:"
echo "1. Note your server IP: $VPN_SERVER_IP"
echo "2. You'll need to generate client certificates"
echo "3. Configure the backend with real certificates"
echo ""
