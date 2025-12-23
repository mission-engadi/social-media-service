#!/bin/bash

# Social Media Service Startup Script
# Port: 8007

set -e

SERVICE_NAME="Social Media Service"
SERVICE_PORT=8007
PID_FILE="/tmp/social_media_service.pid"
LOG_FILE="logs/social_media_service.log"

echo "Starting ${SERVICE_NAME}..."

# Check if service is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "${SERVICE_NAME} is already running (PID: $PID)"
        exit 1
    else
        echo "Removing stale PID file..."
        rm -f "$PID_FILE"
    fi
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the service
echo "Starting ${SERVICE_NAME} on port ${SERVICE_PORT}..."
nohup uvicorn app.main:app --host 0.0.0.0 --port ${SERVICE_PORT} --reload > "$LOG_FILE" 2>&1 &

# Save PID
echo $! > "$PID_FILE"

echo "${SERVICE_NAME} started successfully (PID: $(cat $PID_FILE))"
echo "Logs: $LOG_FILE"
echo "API: http://localhost:${SERVICE_PORT}"
echo "Docs: http://localhost:${SERVICE_PORT}/docs"
