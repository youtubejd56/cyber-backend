# Fix Docker Desktop with WSL

## Step 1: Enable WSL in Docker Desktop

1. Open **Docker Desktop**
2. Go to **Settings** (gear icon)
3. Click **Resources** → **WSL Integration**
4. Enable **Enable integration with additional distros**
5. Make sure your Ubuntu/WSL is checked
6. Click **Apply & Restart**

## Step 2: In WSL Terminal, Test Docker

```bash
docker ps
```

If it works, you're done! Try running docker-compose again.

## If Still Not Working

Run Docker directly in WSL:

```bash
# Start Docker service
sudo service docker start

# Check status
docker ps
```

## Alternative: Use Docker Without Docker Desktop

If Docker Desktop keeps failing, install Docker directly in WSL:

```bash
sudo apt update
sudo apt install docker.io
sudo service docker start
sudo usermod -aG docker $USER
# Log out and back in
```
