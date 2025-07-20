#!/bin/bash

# EPIC V11 Deployment Script
set -e

ENVIRONMENT=${1:-staging}
COMPOSE_FILE="docker-compose.yml"

echo "🚀 Starting EPIC V11 deployment to $ENVIRONMENT..."

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo "❌ Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo "❌ .env file not found. Please create one with required environment variables."
    exit 1
fi

# Pull latest images
echo "📦 Pulling latest Docker images..."
docker-compose pull

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down

# Start services with health checks
echo "🔄 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to become healthy..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

services=("traefik" "postgres" "redis" "control_panel_backend" "mcp_server" "frontend")

for service in "${services[@]}"; do
    echo "Checking $service..."
    if docker-compose ps -q $service | xargs docker inspect --format='{{.State.Health.Status}}' | grep -q healthy; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service is not healthy"
        docker-compose logs $service
        exit 1
    fi
done

# Run smoke tests
echo "🧪 Running smoke tests..."
if command -v python3 &> /dev/null; then
    pip3 install pytest httpx
    python3 -m pytest tests/smoke/ -v || {
        echo "❌ Smoke tests failed"
        docker-compose logs
        exit 1
    }
    echo "✅ Smoke tests passed"
else
    echo "⚠️ Python3 not found, skipping smoke tests"
fi

# Cleanup old images
echo "🧹 Cleaning up old Docker images..."
docker image prune -f

echo "🎉 Deployment to $ENVIRONMENT completed successfully!"

# Show service URLs
echo ""
echo "📋 Service URLs:"
if [[ "$ENVIRONMENT" == "staging" ]]; then
    echo "Frontend: https://staging.epic.pos.com"
    echo "API: https://staging.epic.pos.com/control"
    echo "Traefik Dashboard: https://staging.epic.pos.com:8080"
else
    echo "Frontend: https://epic.pos.com"
    echo "API: https://epic.pos.com/control"
    echo "Traefik Dashboard: https://epic.pos.com:8080"
fi