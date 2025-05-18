#!/bin/bash

# Setup script for secure MLOps environment

set -e

echo "🚀 Setting up Secure MLOps Environment..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p {workspace,models,logs,data,monitoring,letsencrypt}
mkdir -p code-server/config ml-service

# Generate strong secrets if .env doesn't exist
if [ ! -f .env ]; then
    echo "🔐 Generating secrets..."
    JWT_SECRET=$(openssl rand -hex 32)
    REDIS_PASSWORD=$(openssl rand -hex 16)
    
    cat > .env << EOF
# Environment variables for docker-compose
JWT_SECRET_KEY=${JWT_SECRET}
REDIS_PASSWORD=${REDIS_PASSWORD}
EOF
    echo "✓ Secrets generated in .env file"
fi

# Set proper permissions
echo "🔒 Setting permissions..."
chmod 600 .env
chmod 755 workspace
chmod 755 models
chmod 755 logs

# Add local domain entries for HTTPS testing
# Commented out to avoid modifying system files
# echo "🌐 Adding local domains to /etc/hosts..."
# if ! grep -q "dev.localhost" /etc/hosts; then
#     echo "Adding local domain entries..."
#     echo "127.0.0.1 dev.localhost api.localhost metrics.localhost" | sudo tee -a /etc/hosts
# fi

# Using Docker's internal DNS instead
echo "🌐 Using Docker's internal DNS for domain resolution..."


# Create sample training data
echo "📊 Creating sample data..."
cat > workspace/create_sample_data.py << 'EOF'
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris

# Load iris dataset and save as CSV for demonstration
iris = load_iris()
df = pd.DataFrame(iris.data, columns=iris.feature_names)
df['target'] = iris.target
df['target_name'] = [iris.target_names[i] for i in iris.target]

# Save to data directory
df.to_csv('../code-server/data/iris_dataset.csv', index=False)
print("Sample dataset created at code-server/data/iris_dataset.csv")
EOF

# Build and start the environment
echo "🚢 Building Docker containers..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

echo """
✅ Setup complete!

Access your development environment:
🔗 Code Server (IDE): https://dev.localhost (password: secure_dev_password_123, port: 8443)
🔗 ML API: https://api.localhost
🔗 Metrics: https://metrics.localhost
🔗 Traefik Dashboard: http://localhost:8080

Next steps:
1. Open https://dev.localhost in your browser
2. Run workspace/train_model.py to train the initial model
3. Test the API with workspace/test_client.py
4. Monitor metrics at https://metrics.localhost

Security features implemented:
✓ HTTPS everywhere with Traefik
✓ JWT authentication
✓ Rate limiting
✓ Model integrity checks
✓ Non-root containers
✓ Network segmentation
✓ Audit logging
✓ Prometheus monitoring

Note: For production, replace self-signed certificates with real ones!
"""