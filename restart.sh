#!/bin/bash

# Social Media Service Restart Script

set -e

SERVICE_NAME="Social Media Service"

echo "Restarting ${SERVICE_NAME}..."

# Stop the service
./stop.sh

# Wait a moment
sleep 2

# Start the service
./start.sh

echo "${SERVICE_NAME} restarted successfully"
