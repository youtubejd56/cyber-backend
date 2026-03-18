# True TryHackMe Setup Guide

To get real TryHackMe/HackTheBox style access (VPN → lab machines), you need ALL services running in WSL, not Docker Desktop.

## Architecture

```
┌──────────────┐     ┌─────────────────────────┐
│ Your PC      │     │ WSL (Ubuntu)            │
│              │     │                         │
│ OpenVPN      │────▶│  ┌─────────────────┐    │
│ Client       │     │  │ OpenVPN Server  │    │
│              │     │  │ (10.8.0.x)      │    │
└──────────────┘     │  └────────┬────────┘    │
                     │           │             │
                     │  ┌────────▼────────┐    │
                     │  │ Docker         │    │
                     │  │ Lab Machines   │    │
                     │  │ (10.10.10.x)  │    │
                     │  └─────────────────┘    │
                     └─────────────────────────┘
```

## Step 1: Install Docker in WSL

```bash
# In WSL (not Docker Desktop!)
sudo apt update
sudo apt install docker.io docker-compose-v2

# Start Docker
sudo service docker start

# Enable docker in WSL2
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker
```

## Step 2: Start Lab Machines in WSL Docker

```bash
# Create lab network
docker network create --subnet=10.10.10.0/24 lab_network

# Run a vulnerable machine
docker run -d --network lab_network --name lab1 vulnerables/web-dvwa
```

## Step 3: Set Up OpenVPN in WSL

```bash
cd /mnt/c/Users/windows/Desktop/cyber_training
sudo bash scripts/setup_openvpn.sh
```

## Step 4: Create Client Config

```bash
sudo bash scripts/create_client.sh myuser
```

## Step 5: Copy .ovpn to Windows and Connect

```bash
# Copy from WSL to Windows
cp /etc/openvpn/client-configs/myuser.ovpn /mnt/c/Users/windows/Desktop/

# In Windows: Import to OpenVPN Connect and connect
```

Now when you ping 10.10.10.3, it should work!

## Key Point

The secret is: **Everything must be in WSL**
- OpenVPN in WSL
- Docker in WSL (not Docker Desktop)
- Lab machines in WSL's Docker

Then the VPN can reach the containers because they're all on the same Linux network.
