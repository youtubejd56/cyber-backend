#!/bin/bash
# Generate OpenVPN Client Configuration
# Usage: sudo bash create_client.sh <username>

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo bash create_client.sh <username>"
    exit 1
fi

if [ -z "$1" ]; then
    echo "Usage: sudo bash create_client.sh <username>"
    exit 1
fi

USERNAME="$1"
EASY_RSA_DIR="/etc/openvpn/easy-rsa"
OVPN_DIR="/etc/openvpn/client-configs"
CCD_DIR="/etc/openvpn/ccd"

mkdir -p $OVPN_DIR

echo "=========================================="
echo "Creating VPN config for: $USERNAME"
echo "=========================================="

# Get server IP
SERVER_IP=$(curl -s ifconfig.me || hostname -I | awk '{print $1}')
PORT=1194
PROTO="udp"

cd $EASY_RSA_DIR

# Generate client certificate
echo "[1/3] Generating client certificate..."
./easyrsa build-client-full "$USERNAME" nopass

# Get VPN network
VPN_NETWORK=$(grep "^server" /etc/openvpn/server.conf | awk '{print $2}')
VPN_NETMASK=$(grep "^server" /etc/openvpn/server.conf | awk '{print $3}')

# Assign client IP from pool (10.8.0.x)
CLIENT_IP="10.8.0.$(shuf -i 2-254 -n 1)"

# Create CCD file for static IP
echo "[2/3] Assigning static IP: $CLIENT_IP"
cat > $CCD_DIR/$USERNAME <<EOF
ifconfig-push $CLIENT_IP 255.255.255.0
iroute 10.10.10.0 255.255.255.0
EOF

# Generate client OVPN file
echo "[3/3] Creating client config file..."

# Get certificates
CA_CERT=$(cat $EASY_RSA_DIR/pki/ca.crt)
CLIENT_CERT=$(cat $EASY_RSA_DIR/pki/issued/$USERNAME.crt)
CLIENT_KEY=$(cat $EASY_RSA_DIR/pki/private/$USERNAME.key)
TA_KEY=$(cat $EASY_RSA_DIR/pki/ta.key)

cat > $OVPN_DIR/$USERNAME.ovpn <<EOF
# CyberTraining Lab VPN Configuration
# Generated for: $USERNAME
# Server: $SERVER_IP:$PORT

client
dev tun
proto $PROTO
remote $SERVER_IP $PORT
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
$CA_CERT
</ca>

<cert>
$CLIENT_CERT
</cert>

<key>
$CLIENT_KEY
</key>

<tls-auth>
$TA_KEY
</tls-auth>
key-direction 1

# Keep alive
keepalive 10 60
EOF

echo ""
echo "=========================================="
echo "Client config created successfully!"
echo "=========================================="
echo "Config file: $OVPN_DIR/$USERNAME.ovpn"
echo "Username: $USERNAME"
echo "Password: (none - certificate-based auth)"
echo ""
echo "Download the .ovpn file and import to your OpenVPN client."
echo ""
