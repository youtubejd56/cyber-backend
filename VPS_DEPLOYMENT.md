# VPS Deployment Guide

## Step 1: Buy a VPS
Get a cheap VPS from:
- **DigitalOcean** - droplets starting at $4/month
- **Linode** - starting at $5/month  
- **AWS EC2** - free tier available
- **Google Cloud** - free tier available

Choose Ubuntu 20.04 or 22.04 as the operating system.

## Step 2: Connect to Your VPS
```bash
ssh root@your_server_ip
```

## Step 3: Install Docker
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Start Docker
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

## Step 4: Upload Your Project
Upload your project folder to the VPS using:
```bash
# From your local computer:
scp -r cyber_training root@your_server_ip:/root/
```

Or use Git:
```bash
# On VPS:
git clone https://github.com/youtubejd56/cyber-backend.git
git clone https://github.com/youtubejd56/cyber-frontend.git
```

## Step 5: Run the Application
```bash
cd cyber_training
docker-compose up -d
```

## Step 6: Access Your App
- Frontend: http://your_server_ip:3001
- Backend: http://your_server_ip:8000

## Important Notes
- The docker-compose.yml mounts `/var/run/docker.sock` so the backend can create containers
- For production, add a domain name and configure HTTPS with Nginx
- Keep the server running 24/7

## Troubleshooting
```bash
# Check if containers are running
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```
