#!/bin/bash
set -e

# Stop and remove existing containers
docker-compose stop prometheus grafana
docker-compose rm -f prometheus grafana

# Remove volumes to start fresh
# Note: This will delete all monitoring data!
docker volume rm -f secured-mlops_prometheus_data

docker volume rm -f secured-mlops_grafana_data

# Recreate and start the services
docker-compose up -d prometheus grafana

echo "Monitoring services have been restarted with fresh data
echo "Grafana: https://dashboard.localhost:9443"
echo "Prometheus: https://metrics.localhost:9443"
