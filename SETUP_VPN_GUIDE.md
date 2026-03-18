# Cyber Training Platform - VPN & Lab Access Setup Guide

This guide explains how to set up VPN and lab access like HackTheBox.

## The Problem

Your current setup only generates **placeholder VPN configs** - they don't actually work because:
1. No real OpenVPN server is running
2. No certificates are configured
3. No Docker host for vulnerable machines

## Solution: Full Setup

### Step 1: Set Up OpenVPN Server on Your Linux Server

```bash
# Upload and run the setup script
chmod +x scripts/setup_openvpn.sh
sudo bash scripts/setup_openvpn.sh
```

The script will:
- Install OpenVPN and EasyRSA
- Generate CA and server certificates
- Configure VPN network (10.8.0.0/24)
- Set up routing to lab network (10.10.10.0/24)
- Start the OpenVPN service

**Important**: Note your server's public IP after setup!

### Step 2: Update Your Server IP in Environment

```bash
# Set your server's public IP
export VPN_SERVER_IP="your.server.public.ip"

# Or update docker-compose.full.yml with your IP
```

### Step 3: Run Full Docker Stack

```bash
# Use the full compose file with lab network
docker-compose -f docker-compose.full.yml up -d
```

### Step 4: Generate Client Configs for Users

When users register and want VPN access:

```bash
# Create client certificate and config
sudo bash scripts/create_client.sh username
```

This creates:
- Client certificate in `/etc/openvpn/pki/`
- Client config file in `/etc/openvpn/client-configs/username.ovpn`
- Static IP assignment in `/etc/openvpn/ccd/username`

### Step 5: Connect from Client Machine

1. **Download the .ovpn file** from `/etc/openvpn/client-configs/` on server
2. **Install OpenVPN client**:
   ```bash
   # Linux
   sudo apt install openvpn
   
   # macOS
   brew install openvpn
   
   # Windows - download from openvpn.net
   ```
3. **Connect**:
   ```bash
   sudo openvpn --config username.ovpn
   ```

### Step 6: Access Lab Machines

Once VPN is connected:

```bash
# SSH to lab machines (example)
ssh user@10.10.10.5

# Find flags
cat /home/user/user.txt
cat /root/root.txt
```

## Quick Test (Local Machine)

For testing locally without a real VPN server:

```bash
# Start local OpenVPN for testing
sudo apt install openvpn

# Create a test server config locally
# (Use scripts/setup_openvpn.sh on same machine)

# Generate test client
sudo bash scripts/create_client.sh testuser

# Connect
sudo openvpn --config /etc/openvpn/client-configs/testuser.ovpn
```

## Network Architecture

```
┌─────────────┐         ┌──────────────────┐
│  User       │         │  Linux Server    │
│  Machine    │────────▶│                  │
│             │  VPN    │  ┌────────────┐  │
└─────────────┘         │  │ OpenVPN    │  │
                        │  │ Server     │  │
                        │  └────────────┘  │
                        │         │         │
                        │  ┌────────────┐  │
                        │  │ Docker Host │  │
                        │  │ (Machines)  │  │
                        │  └────────────┘  │
                        │   10.10.10.0/24  │
                        └──────────────────┘
```

## Troubleshooting

### VPN Won't Connect
1. Check firewall: `sudo ufw allow 1194/udp`
2. Check OpenVPN status: `sudo systemctl status openvpn@server`
3. Check logs: `sudo journalctl -u openvpn@server -f`

### Can't Reach Lab Machines
1. Verify IP forwarding: `cat /proc/sys/net/ipv4/ip_forward` (should be 1)
2. Check iptables: `sudo iptables -t nat -L -n`
3. Verify Docker network exists: `docker network ls`

### Backend Can't Generate Certs
1. Ensure EasyRSA is installed: `which easyrsa`
2. Check permissions: `ls -la /etc/openvpn/pki/`
3. Run backend as privileged or use host OpenVPN

## Files Created

| File | Purpose |
|------|---------|
| `scripts/setup_openvpn.sh` | Sets up OpenVPN server |
| `scripts/create_client.sh` | Creates client certificates |
| `backend/openvpn_manager.py` | Python module for VPN management |
| `docker-compose.full.yml` | Full stack with lab network |

## Alternative: Use OpenVPN Access Server

For easier management, consider OpenVPN Access Server:
```bash
# Install OpenVPN AS (Ubuntu)
wget https://as-releases.openvpn.net/as/openvpn-as-3.3.0-Ubuntu20.amd64.deb
sudo dpkg -i openvpn-as-3.3.0-Ubuntu20.amd64.deb
# Then access admin panel at https://your-ip:943
```
