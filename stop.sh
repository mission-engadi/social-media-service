#!/bin/bash

# Social Media Service Stop Script

set -e

SERVICE_NAME="Social Media Service"
PID_FILE="/tmp/social_media_service.pid"

echo "Stopping ${SERVICE_NAME}..."

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "${SERVICE_NAME} is not running (no PID file found)"
    exit 0
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "${SERVICE_NAME} is not running (stale PID file)"
    rm -f "$PID_FILE"
    exit 0
fi

# Stop the process
echo "Stopping process (PID: $PID)..."
kill "$PID"

# Wait for process to stop
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "${SERVICE_NAME} stopped successfully"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if still running
echo "Force stopping process..."
kill -9 "$PID" 2>/dev/null || true
rm -f "$PID_FILE"
echo "${SERVICE_NAME} stopped"
