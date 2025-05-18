#!/bin/bash

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Setting up ML development environment"

# Fix permissions
chown -R abc:abc /config
chmod -R 755 /config

# Install Python packages
log "Installing Python packages"
apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install required Python packages
log "Installing Python ML packages"
pip3 install --break-system-packages requests numpy pandas scikit-learn

# Create connectivity test script
cat > /config/workspace/test_connectivity.sh << 'EOF'
#!/bin/bash
python3 /config/workspace/test_api_connection.py
EOF

chmod +x /config/workspace/test_connectivity.sh
chown abc:abc /config/workspace/test_connectivity.sh

log "Setup complete! You can test connectivity by running ./test_connectivity.sh"
