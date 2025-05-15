#!/bin/bash
# Generate secure environment file with random passwords
# This script creates a proper .env file from .env.template with secure random passwords

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Generating secure .env file for MLOps setup...${NC}"

# Check if .env.template exists
if [ ! -f .env.template ]; then
  echo -e "${RED}Error: .env.template not found!${NC}"
  exit 1
fi

# Create .env file from template
cp .env.template .env

# Generate random secure passwords
JWT_SECRET=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 20)
CODE_SERVER_PASSWORD="secure_dev_password_123" # Keep existing password
GRAFANA_PASSWORD="admin" # Keep existing password
TRAEFIK_PASSWORD="admin" # Keep existing password
PROMETHEUS_PASSWORD="metrics" # Keep existing password

# Update .env file with generated passwords
sed -i '' "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$JWT_SECRET|g" .env
sed -i '' "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=$REDIS_PASSWORD|g" .env
sed -i '' "s|CODE_SERVER_PASSWORD=.*|CODE_SERVER_PASSWORD=$CODE_SERVER_PASSWORD|g" .env
sed -i '' "s|GRAFANA_PASSWORD=.*|GRAFANA_PASSWORD=$GRAFANA_PASSWORD|g" .env
sed -i '' "s|TRAEFIK_DASHBOARD_PASSWORD=.*|TRAEFIK_DASHBOARD_PASSWORD=$TRAEFIK_PASSWORD|g" .env
sed -i '' "s|PROMETHEUS_PASSWORD=.*|PROMETHEUS_PASSWORD=$PROMETHEUS_PASSWORD|g" .env

# Generate bcrypt hashes for HTTP Basic Auth
echo -e "${BLUE}Generating password hashes for HTTP Basic Auth...${NC}"

# Generate admin:admin hash for Traefik dashboard
TRAEFIK_HASH=$(htpasswd -nbB admin "$TRAEFIK_PASSWORD" | sed -e "s/\\$/\\$\\$/g")
# Generate metrics:metrics hash for Prometheus
PROMETHEUS_HASH=$(htpasswd -nbB metrics "$PROMETHEUS_PASSWORD" | sed -e "s/\\$/\\$\\$/g")

# Store hashes in .env for docker-compose to use
echo "" >> .env
echo "# Generated password hashes (for docker-compose)" >> .env
echo "TRAEFIK_DASHBOARD_AUTH=$TRAEFIK_HASH" >> .env
echo "PROMETHEUS_AUTH=$PROMETHEUS_HASH" >> .env

echo -e "${GREEN}Environment file generated successfully!${NC}"
echo -e "${BLUE}Service credentials:${NC}"
echo -e "Code Server: ${GREEN}secure_dev_password_123${NC}"
echo -e "Grafana: ${GREEN}admin:admin${NC}"
echo -e "Traefik Dashboard: ${GREEN}admin:admin${NC}"
echo -e "Prometheus: ${GREEN}metrics:metrics${NC}"
echo ""
echo -e "${BLUE}To apply these settings, run:${NC}"
echo -e "${GREEN}make rebuild${NC}"

chmod +x generate-env.sh
