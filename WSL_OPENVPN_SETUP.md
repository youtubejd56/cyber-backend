# Setting Up OpenVPN Server Using WSL on Windows

This guide explains how to run an OpenVPN server inside WSL (Windows Subsystem for Linux) so you can connect via VPN and access lab machines.

## Prerequisites

1. **WSL installed** - Run `wsl --install` in PowerShell as Administrator
2. **Ubuntu** - Install from Microsoft Store
3. **Docker Desktop** - Ensure Docker is configured to integrate with WSL

## Step 1: Open WSL Terminal

```powershell
wsl -d Ubuntu
```

## Step 2: Run the OpenVPN Setup Script

```bash
cd /mnt/c/Users/windows/Desktop/cyber_training
sudo bash scripts/setup_openvpn.sh
```

**Note**: During setup, you'll need to:
- Press Enter for default certificate values
- Set a password for the CA

## Step 3: Get Server IP

```bash
# Get your Windows host IP (accessible from WSL)
ip route | grep default | awk '{print $3}'
```

Or in PowerShell:
```powershell
ipconfig
```
Look for Ethernet adapter vEthernet (WSL).

## Step 4: Configure Client Access

For each user, create a client certificate:

```bash
sudo bash scripts/create_client.sh username
```

This generates: `/etc/openvpn/client-configs/username.ovpn`

## Step 5: Copy .ovpn to Windows

```bash
# Copy to a Windows-accessible location
cp /etc/openvpn/client-configs/username.ovpn /mnt/c/Users/windows/Desktop/
```

## Step 6: Connect from Windows

1. Install [OpenVPN Connect](https://openvpn.net/client/)
2. Import the .ovpn file
3. Connect with the credentials

## Important: Network Configuration

For WSL to route traffic to Docker containers:

```bash
# In WSL, allow IP forwarding
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward

# Check Docker network
docker network inspect lab_network
```

## Accessing Lab Machines

Once VPN connects, you should get an IP like `10.8.0.x` and be able to ping lab machines at `10.10.10.x`.

## Troubleshooting

**VPN connects but can't reach 10.10.10.x:**
- WSL may need special routing
- Docker containers must be on `lab_network`

**Can't bind to port 1194:**
- Use a different port or check if port is in use

**Alternative: Use direct access instead of VPN:**
- Access lab machines via localhost ports directly
- No VPN needed for local testing
