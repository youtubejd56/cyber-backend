# Fix VPN to Ping Machines from WSL

The problem: Docker Desktop and WSL have separate networks - they can't communicate.

## Solution: Use WSL Docker (Not Docker Desktop)

### Step 1: In Kali WSL Terminal

```bash
# Stop Docker Desktop on Windows first!

# Start Docker in WSL
sudo service docker start

# Create network in WSL Docker
docker network create --subnet=10.10.10.0/24 lab_network

# Start vulnerable machine in WSL Docker
docker run -d --network lab_network --name lab1 vulnerables/web-dvwa
```

### Step 2: Check the IP

```bash
docker inspect lab1 --format '{{.NetworkSettings.Networks.lab_network.IPAddress}}'
```

### Step 3: From Another WSL Terminal (with VPN)

```bash
# Connect VPN first
sudo openvpn --config /path/to/your.ovpn

# Ping the lab machine
ping 10.10.10.2
```

## Key Points

1. **Close Docker Desktop** on Windows - it conflicts with WSL Docker
2. **Use WSL Docker** for lab machines
3. **Both OpenVPN and Docker in WSL** = same network = works!

## Quick Command to Start Everything in WSL

```bash
# In Kali WSL
sudo service docker start
docker network create --subnet=10.10.10.0/24 lab_network 2>/dev/null
docker run -d --network lab_network --name lab1 vulnerables/web-dvwa
docker run -d --network lab_network --name lab2 vulnerables/web-dvwa
# ... add more machines
```

Then connect VPN and ping 10.10.10.x!
