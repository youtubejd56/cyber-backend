# The Problem

You're pinging from WSL (Kali), but your lab containers are running in Docker Desktop (Windows). They're on completely separate networks!

- **Docker Desktop containers**: `lab_u4_m12`, `lab_u4_m3` (Windows)
- **Your ping from WSL**: Can't reach Docker Desktop network

# Solution: Run Lab Machines in WSL Docker

## Step 1: Start Docker in WSL (not Docker Desktop!)

In your **Kali WSL terminal**:

```bash
# Make sure Docker service is running
sudo service docker start

# Check Docker is running
docker ps
```

## Step 2: Create Lab Network in WSL

```bash
docker network create --subnet=10.10.10.0/24 lab_network
```

## Step 3: Start Lab Machine in WSL

```bash
# Remove old container if exists
docker rm -f lab1

# Start new vulnerable machine in WSL Docker
docker run -d --network lab_network --name lab1 vulnerables/web-dvwa
```

## Step 4: Check the IP

```bash
docker inspect lab1 --format '{{.NetworkSettings.Networks.lab_network.IPAddress}}'
```

## Step 5: Now Ping from WSL (after VPN connects)

```bash
ping 10.10.10.x
```

## Why This Works

- **Before**: Docker Desktop (Windows) ≠ WSL (Linux) = Separate networks
- **After**: OpenVPN + Docker both in WSL = Same network = Can ping!
