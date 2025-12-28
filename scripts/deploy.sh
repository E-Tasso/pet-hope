#!/bin/bash
# PetHope - Deploy Script for VPS
# Usage: ./deploy.sh [domain]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Please don't run as root. Run as the pethope user."
    exit 1
fi

# Get domain from argument or ask
DOMAIN=${1:-""}
if [ -z "$DOMAIN" ]; then
    read -p "Enter your domain (e.g., pethope.com.br): " DOMAIN
fi

if [ -z "$DOMAIN" ]; then
    log_error "Domain is required"
    exit 1
fi

log_info "Deploying PetHope to $DOMAIN"

# Check if .env exists
if [ ! -f .env ]; then
    log_info "Creating .env from example..."
    cp .env.example .env

    # Generate secrets
    SECRET_KEY=$(openssl rand -hex 32)
    POSTGRES_PASSWORD=$(openssl rand -hex 16)
    MINIO_PASSWORD=$(openssl rand -hex 16)
    ADMIN_PASSWORD=$(openssl rand -hex 12)

    # Update .env
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
    sed -i "s/MINIO_ROOT_PASSWORD=.*/MINIO_ROOT_PASSWORD=$MINIO_PASSWORD/" .env
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    sed -i "s/ADMIN_PASSWORD=.*/ADMIN_PASSWORD=$ADMIN_PASSWORD/" .env
    sed -i "s/ALLOWED_ORIGINS=.*/ALLOWED_ORIGINS=https:\/\/$DOMAIN,https:\/\/www.$DOMAIN/" .env
    sed -i "s/NUXT_PUBLIC_API_BASE=.*/NUXT_PUBLIC_API_BASE=https:\/\/$DOMAIN\/api/" .env
    sed -i "s/MINIO_PUBLIC_URL=.*/MINIO_PUBLIC_URL=https:\/\/$DOMAIN\/storage/" .env
    sed -i "s/ENVIRONMENT=.*/ENVIRONMENT=production/" .env

    log_info "Generated secure passwords. Check .env file."
    log_warn "Save the ADMIN_PASSWORD: $ADMIN_PASSWORD"
fi

# Create production nginx config
log_info "Creating nginx production config..."
if [ ! -f nginx/conf.d/prod.conf ]; then
    cp nginx/conf.d/prod.conf.example nginx/conf.d/prod.conf
    sed -i "s/DOMAIN/$DOMAIN/g" nginx/conf.d/prod.conf
    log_info "Created nginx/conf.d/prod.conf for $DOMAIN"
fi

# Check if SSL certificates exist
SSL_CERT="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
if [ ! -f "$SSL_CERT" ]; then
    log_warn "SSL certificate not found. Starting without SSL first..."

    # Create temporary nginx config without SSL
    cat > nginx/conf.d/temp.conf << EOF
upstream backend { server backend:8000; }
upstream frontend { server frontend:3000; }
upstream minio { server minio:9000; }

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location /health { return 200 "healthy"; add_header Content-Type text/plain; }
    location /api/ { proxy_pass http://backend/api/; }
    location /storage/ { proxy_pass http://minio/pethope-images/; }
    location / { proxy_pass http://frontend; }
}
EOF

    # Start services with temp config
    docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

    log_info "Services started. Now run certbot to get SSL certificate:"
    echo ""
    echo "  sudo certbot certonly --webroot -w /var/www/certbot -d $DOMAIN -d www.$DOMAIN"
    echo ""
    echo "After getting the certificate, run this script again."
    exit 0
fi

# SSL exists, deploy with full config
log_info "SSL certificate found. Deploying with HTTPS..."

# Remove temp config if exists
rm -f nginx/conf.d/temp.conf

# Build and start
log_info "Building and starting containers..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Wait for services
log_info "Waiting for services to be ready..."
sleep 10

# Health check
log_info "Running health checks..."
if curl -sf "http://localhost/health" > /dev/null; then
    log_info "Health check passed!"
else
    log_error "Health check failed. Check logs with: docker compose logs"
    exit 1
fi

# Done
echo ""
log_info "========================================="
log_info " PetHope deployed successfully!"
log_info "========================================="
echo ""
echo "  Website: https://$DOMAIN"
echo "  API:     https://$DOMAIN/api"
echo "  Docs:    https://$DOMAIN/docs"
echo ""
log_info "Commands:"
echo "  View logs:    docker compose logs -f"
echo "  Restart:      docker compose restart"
echo "  Stop:         docker compose down"
echo ""
