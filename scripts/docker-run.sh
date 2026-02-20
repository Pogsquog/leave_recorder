#!/bin/bash
set -e

echo "=== Running Holiday Holliday in Docker ==="

# Build and run with docker-compose
echo "Building containers..."
docker compose build

echo ""
echo "Starting services..."
echo "App will be available at http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

docker compose up app

# Cleanup on exit
trap "echo ''; echo 'Stopping containers...'; docker compose down" EXIT
