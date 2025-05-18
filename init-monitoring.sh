#!/bin/bash
set -e

# Create directories for Prometheus and Grafana
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p monitoring/prometheus

# Set proper permissions
chmod -R 777 monitoring/grafana/provisioning/dashboards
chmod -R 777 monitoring/grafana/provisioning/datasources
chmod -R 777 monitoring/prometheus

# Create Prometheus config if it doesn't exist
if [ ! -f monitoring/prometheus/prometheus.yml ]; then
    cat > monitoring/prometheus/prometheus.yml << 'EOL'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'ml-api'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['ml-api:8000']
    scrape_interval: 5s

  - job_name: 'traefik'
    static_configs:
      - targets: ['traefik:8080']
    metrics_path: '/metrics'
EOL
fi

echo "Monitoring setup complete!"
