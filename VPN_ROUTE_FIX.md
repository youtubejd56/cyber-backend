# Add Route to Docker Network from VPN

Now that you have the IP `172.24.0.1`, you need to tell the VPN to route traffic to the Docker network.

## In WSL, add route to Docker network:

```bash
# Add route so VPN clients can reach Docker containers
sudo ip route add 172.24.0.0/24 via 172.24.0.1

# Or add to lab network (if different)
sudo ip route add 10.10.10.0/24 via 172.24.0.1
```

## Also update OpenVPN server config:

```bash
# Edit OpenVPN server config
sudo nano /etc/openvpn/server.conf

# Add this line to push route to clients:
push "route 172.24.0.0 255.255.255.0"
push "route 10.10.10.0 255.255.255.0"

# Restart OpenVPN
sudo service openvpn restart
```

## Alternative: Check Docker network in WSL:

```bash
# See what Docker networks exist
docker network ls

# Inspect the bridge network
docker network inspect bridge
```

Look for the Gateway IP - that's where you route traffic to.
