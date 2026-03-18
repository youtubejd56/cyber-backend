#!/bin/bash
# Run this from Kali WSL
# Usage: sudo bash run_openvpn.sh

echo "Setting up OpenVPN server..."

# Navigate to the project folder
cd /mnt/c/Users/windows/Desktop/cyber_training

# Run the setup script
sudo bash scripts/setup_openvpn.sh
