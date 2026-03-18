#!/bin/bash
# Docker Build and Push Script for Cyber Training Platform

echo "========================================"
echo "Building Cyber Training Platform Images"
echo "========================================"

# Build and start the containers
echo ""
echo "Building and starting containers..."
docker-compose up --build

echo ""
echo "========================================"
echo "Cyber Training Platform is running!"
echo "========================================"
echo "Backend API: http://localhost:8000"
echo "Frontend:    http://localhost:3000"
echo "========================================"
