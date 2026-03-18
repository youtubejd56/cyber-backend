# Troubleshooting: VPN Connects But Can't Ping Lab Machines

This happens because the Docker containers (lab machines) are not accessible from the WSL/OpenVPN network.

## The Problem

- **OpenVPN server**: Running in WSL (Linux)
- **Docker containers**: Running in Docker Desktop (Windows)
- **Networks**: They're separate - VPN can't reach Docker's network

## Solution: Route Docker Network Through VPN

### Option 1: Run Docker in WSL Instead of Docker Desktop

Instead of using Docker Desktop, run Docker directly in WSL:

```bash
# In WSL
sudo apt update
sudo apt install docker.io
sudo service docker start

# Add user to docker group
sudo usermod -aG docker $USER
```

Then run lab machines in WSL's Docker.

### Option 2: Use Host Network Mode

When starting lab machines, use `--network=host`:

```bash
docker run -d --network=host --name lab1 vulnerables/web-dvwa
```

Then the lab machine shares the WSL network and should be reachable via VPN.

### Option 3: Bridge Networks

Create a Docker network that WSL can route to:

```bash
# In WSL
docker network create --subnet=10.10.10.0/24 lab_network

# Run container on this network
docker run -d --network=lab_network --name lab1 vulnerables/web-dvwa
```

### Option 4: Simplest - Direct Access (No VPN)

For local testing, just access lab machines directly:

- **Web**: http://localhost:PORT (from Django response)
- **SSH**: Use container IP directly

The lab machines are already accessible - you don't need VPN for local testing!

---

## Quick Fix for VPN Routing

Add this route in your OpenVPN config to reach Docker:

```bash
# In WSL, add route to Docker network
sudo ip route add 10.10.10.0/24 via <docker-host-ip>
```

Find Docker host IP from Windows:
```powershell
ipconfig
```
Look for vEthernet (WSL) or Docker Desktop adapter.
