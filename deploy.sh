#!/bin/bash
# Deploy script for Linux server

echo "Loading Docker images..."
docker load -i cyber_training_backend.tar
docker load -i cyber_training_frontend.tar

echo "Starting containers..."
docker-compose up -d

echo "Done!"
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:3000"
