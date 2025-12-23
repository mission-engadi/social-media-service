#!/bin/bash

# Social Media Service Status Script

SERVICE_NAME="Social Media Service"
SERVICE_PORT=8007
PID_FILE="/tmp/social_media_service.pid"

echo "=== ${SERVICE_NAME} Status ==="
echo ""

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "Status: NOT RUNNING (no PID file)"
    exit 1
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is running
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "Status: NOT RUNNING (stale PID file)"
    rm -f "$PID_FILE"
    exit 1
fi

echo "Status: RUNNING"
echo "PID: $PID"
echo "Port: $SERVICE_PORT"
echo ""

# Show process info
echo "Process Information:"
ps -p "$PID" -o pid,ppid,cmd,%mem,%cpu,etime

echo ""
echo "API Endpoint: http://localhost:${SERVICE_PORT}"
echo "Documentation: http://localhost:${SERVICE_PORT}/docs"
echo "Health Check: http://localhost:${SERVICE_PORT}/api/v1/health"

# Check if port is listening
if command -v netstat &> /dev/null; then
    echo ""
    echo "Port Status:"
    netstat -tuln | grep ":${SERVICE_PORT}" || echo "Port ${SERVICE_PORT} not listening"
fi
