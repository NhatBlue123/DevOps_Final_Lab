#!/bin/sh
set -e

COMPOSE_FILE="docker-compose.bluegreen.yml"
NGINX_CONF="nginx/nginx.conf"

# Auto-detect compose command
if command -v docker-compose > /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif docker compose version > /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "ERROR: docker-compose not found!"
    exit 1
fi

echo "=== Initiating Zero-Downtime Blue-Green Deployment ==="
echo "Using compose: $COMPOSE_CMD"

# Generate self-signed SSL cert if not exists
if [ ! -f "certs/nginx.crt" ]; then
    echo "Generating self-signed SSL certificate..."
    mkdir -p certs
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout certs/nginx.key \
        -out certs/nginx.crt \
        -subj "/CN=$(hostname -I | awk '{print $1}')" 2>/dev/null
    echo "SSL certificate generated in certs/"
fi

# Determine current/target slot from nginx.conf
if grep -q "backend_blue:8000" "$NGINX_CONF" 2>/dev/null; then
    CURRENT="blue"
    TARGET="green"
else
    CURRENT="green"
    TARGET="blue"
fi

echo "Current Active: backend_$CURRENT"
echo "Target Slot   : backend_$TARGET"

# Start DB + target backend
echo "Starting db and backend_$TARGET..."
$COMPOSE_CMD -f "$COMPOSE_FILE" up -d db "backend_$TARGET"

# Health check
echo "Verifying health check on backend_$TARGET..."
MAX_ATTEMPTS=15
ATTEMPT=1
HEALTHY=0

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "Attempt $ATTEMPT/$MAX_ATTEMPTS: Checking http://localhost:8000/health..."
    if docker exec "app_backend_$TARGET" curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "backend_$TARGET is HEALTHY!"
        HEALTHY=1
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    sleep 2
done

if [ $HEALTHY -eq 1 ]; then
    echo "Health check passed! Switching traffic to backend_$TARGET..."

    # Update nginx upstream config
    sed -i "s/backend_$CURRENT:8000/backend_$TARGET:8000/g" "$NGINX_CONF"

    # Start router if not running, else reload config
    if docker ps -q -f name=app_router | grep -q .; then
        docker exec app_router nginx -s reload
        echo "Nginx reloaded. Traffic routed to backend_$TARGET!"
    else
        echo "Starting router (nginx)..."
        $COMPOSE_CMD -f "$COMPOSE_FILE" up -d router
        echo "Router started. Traffic routed to backend_$TARGET!"
    fi

    # Stop old slot
    echo "Stopping old slot backend_$CURRENT..."
    docker stop "app_backend_$CURRENT" 2>/dev/null || true
    docker rm   "app_backend_$CURRENT" 2>/dev/null || true

    echo "Zero-Downtime Blue-Green Deployment COMPLETE! Live slot: $TARGET"
else
    echo "HEALTH CHECK FAILED on backend_$TARGET! Initiating ROLLBACK..."
    docker stop "app_backend_$TARGET" 2>/dev/null || true
    docker rm   "app_backend_$TARGET" 2>/dev/null || true
    echo "Rollback complete. backend_$CURRENT remains active."
    exit 1
fi
