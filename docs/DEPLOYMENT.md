# EPIC V11 Deployment Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [GitHub Actions Setup](#github-actions-setup)
- [Environment Configuration](#environment-configuration)
- [Deployment Process](#deployment-process)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Infrastructure Requirements
- **Servers:** Ubuntu 22.04 LTS or newer
- **Docker:** Version 24.0+
- **Docker Compose:** Version 2.20+
- **SSL Certificates:** Let's Encrypt via Traefik
- **Domains:** epic.pos.com (production), staging.epic.pos.com

### Access Requirements
- SSH access to deployment servers
- GitHub repository admin access
- Container registry access (ghcr.io)

## GitHub Actions Setup

### Required Repository Secrets

Navigate to Settings → Secrets and variables → Actions, then add:

#### Staging Environment
```yaml
STAGING_SSH_KEY:     # Private SSH key for staging server
STAGING_USER:        # SSH username (e.g., ubuntu)
STAGING_HOST:        # Staging server IP or hostname
STAGING_URL:         # https://staging.epic.pos.com
```

#### Production Environment
```yaml
PRODUCTION_SSH_KEY:  # Private SSH key for production server
PRODUCTION_USER:     # SSH username (e.g., ubuntu)
PRODUCTION_HOST:     # Production server IP or hostname
PRODUCTION_URL:      # https://epic.pos.com
```

#### Notifications (Optional)
```yaml
SLACK_WEBHOOK:       # Slack webhook URL for deployment notifications
```

### Setting SSH Keys

1. Generate deployment SSH key pair:
```bash
ssh-keygen -t ed25519 -C "epic-deployment" -f epic_deploy_key
```

2. Add public key to server:
```bash
ssh-copy-id -i epic_deploy_key.pub user@server
```

3. Add private key to GitHub secrets:
```bash
cat epic_deploy_key | pbcopy  # Copy to clipboard
# Paste into STAGING_SSH_KEY or PRODUCTION_SSH_KEY
```

## Environment Configuration

### Production .env Template

Create `.env` on production server:

```bash
# Database
POSTGRES_DB=epic_v11_prod
POSTGRES_USER=epic_admin
POSTGRES_PASSWORD=<strong-password>

# Redis
REDIS_PASSWORD=<strong-redis-password>

# Security
JWT_SECRET=<minimum-32-character-secret>
NEXTAUTH_SECRET=<nextauth-secret>
NEXTAUTH_URL=https://epic.pos.com

# AI Services
OPENAI_API_KEY=<your-openai-key>
ANTHROPIC_API_KEY=<your-anthropic-key>
GOOGLE_API_KEY=<your-google-key>

# Monitoring
LANGFUSE_SECRET=<langfuse-secret>
LANGFUSE_SALT=<langfuse-salt>
LANGFUSE_PUBLIC_KEY=<public-key>
LANGFUSE_SECRET_KEY=<secret-key>

# n8n
N8N_USER=admin
N8N_PASSWORD=<n8n-password>

# Environment
NODE_ENV=production
ENVIRONMENT=production
```

### Server Setup Script

Run on fresh server:

```bash
#!/bin/bash
# setup-server.sh

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create app directory
sudo mkdir -p /opt/epic11gemini
sudo chown $USER:$USER /opt/epic11gemini

# Clone repository
cd /opt
git clone https://github.com/NYCip/epic11gemini.git

# Setup firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo "Server setup complete! Please log out and back in for Docker permissions."
```

## Deployment Process

### Automatic Deployment

#### Staging (Continuous)
Every push to `master` branch triggers staging deployment:
1. CI Pipeline runs tests
2. Docker images are built
3. Images pushed to ghcr.io
4. Staging server pulls and deploys
5. Health checks verify deployment
6. Smoke tests run

#### Production (Tag-based)
Create a release tag to deploy to production:

```bash
# Create and push tag
git tag -a v11.0.1 -m "Release v11.0.1 - Feature improvements"
git push origin v11.0.1

# This triggers:
# 1. Staging deployment first
# 2. Production deployment after staging succeeds
# 3. Health checks and smoke tests
# 4. Slack notification
```

### Manual Deployment

#### Deploy to Staging
```bash
ssh user@staging.epic.pos.com
cd /opt/epic11gemini
./scripts/deploy.sh staging
```

#### Deploy to Production
```bash
ssh user@epic.pos.com
cd /opt/epic11gemini
./scripts/deploy.sh production
```

### Zero-Downtime Deployment

The deployment process ensures zero downtime:
1. New containers are started with health checks
2. Traefik routes traffic after health checks pass
3. Old containers are stopped after new ones are healthy
4. Database migrations run in pre-deployment phase

## Rollback Procedures

### Automatic Rollback
If deployment fails, automatic rollback is triggered:
- Health checks fail → Previous version restored
- Smoke tests fail → Previous version restored
- Database migration fails → Transaction rollback

### Manual Rollback

#### Quick Rollback (Last Known Good)
```bash
ssh user@production.epic.pos.com
cd /opt/epic11gemini

# View recent commits
git log --oneline -10

# Rollback to specific commit
git checkout <commit-hash>
docker-compose up -d --force-recreate
```

#### Database Rollback
```bash
# Connect to production database
docker exec -it epic_postgres psql -U epic_admin -d epic_v11

# Restore from backup
docker exec -i epic_postgres pg_restore -U epic_admin -d epic_v11 < backup.sql
```

### Emergency Procedures

#### Edward Override Activation
```bash
# Activate system halt
docker exec -it epic_redis redis-cli
> AUTH <redis-password>
> SET EDWARD_OVERRIDE_STATUS HALT
> EXIT

# All services will refuse to start
```

#### Complete System Restart
```bash
# Stop all services
docker-compose down

# Clear volumes (CAUTION: Data loss)
docker-compose down -v

# Restart fresh
docker-compose up -d
```

## Troubleshooting

### Common Issues

#### 1. Docker Build Failures
```bash
# Clear Docker cache
docker system prune -af
docker volume prune -f

# Rebuild without cache
docker-compose build --no-cache
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL logs
docker logs epic_postgres

# Test connection
docker exec -it epic_postgres pg_isready -U epic_admin

# Reset connections
docker-compose restart postgres
```

#### 3. SSL Certificate Issues
```bash
# Check Traefik logs
docker logs epic_traefik

# Renew certificates
docker exec epic_traefik traefik version
rm -rf ./certificates/acme.json
docker-compose restart traefik
```

#### 4. Service Health Check Failures
```bash
# Check specific service
docker-compose ps
docker logs <service-name>

# Manual health check
curl http://localhost:8000/health
```

### Monitoring Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f agno_service

# System resources
docker stats

# Database connections
docker exec -it epic_postgres psql -U epic_admin -c "SELECT count(*) FROM pg_stat_activity;"
```

### Performance Tuning

#### PostgreSQL Optimization
```sql
-- Increase connections
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '1GB';

-- Restart to apply
docker-compose restart postgres
```

#### Redis Optimization
```bash
# Edit redis command in docker-compose.yml
redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

## Support

- **Logs Location:** `/opt/epic11gemini/logs/`
- **Backups:** Daily at 2 AM UTC to `/backups/`
- **Monitoring:** Langfuse dashboard at `https://langfuse.epic.pos.com`
- **Alerts:** Configured in n8n workflows

For emergency support, check the Edward Override status first:
```bash
docker exec -it epic_redis redis-cli GET EDWARD_OVERRIDE_STATUS
```