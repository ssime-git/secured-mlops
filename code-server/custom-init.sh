#!/bin/bash

# Install Python and required dependencies
apt-get update
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Create a Python virtual environment in a user-writable location
VENV_PATH="/home/abc/venv"
mkdir -p "$VENV_PATH"
chown -R abc:abc "$VENV_PATH"

# Create virtualenv as the abc user
sudo -u abc python3 -m venv "$VENV_PATH"

# Install Python packages as the abc user
sudo -u abc "$VENV_PATH/bin/pip" install --no-cache-dir \
    requests \
    pytest \
    pytest-cov \
    python-dotenv

# Create a symlink for easy access
ln -sf "$VENV_PATH/bin/python3" /usr/local/bin/py3
ln -sf "$VENV_PATH/bin/pip" /usr/local/bin/pip3

# Install Docker CLI
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker CE CLI
apt-get update
apt-get install -y docker-ce-cli

# Create a wrapper script for Python that uses the virtual environment
echo '#!/bin/bash
. /opt/venv/bin/activate
python3 "$@"' > /usr/local/bin/py
chmod +x /usr/local/bin/py

# Ensure the virtual environment is accessible

# Create docker group and add code-server user
groupadd -f docker
usermod -aG docker abc

# Add Python to the PATH for all users
echo "export PATH=\"$VENV_PATH/bin:\$PATH\"" > /etc/profile.d/python-venv.sh
chmod +x /etc/profile.d/python-venv.sh

# Create a wrapper script for the code-server user
cat > /usr/local/bin/py << 'EOL'
#!/bin/bash
source "$HOME/venv/bin/activate"
exec python3 "$@"
EOL
chmod +x /usr/local/bin/py
chown abc:abc /usr/local/bin/py

# Set proper permissions for the code-server user
chown -R abc:abc /config/workspace

# Create a .bashrc for the code-server user
CODE_USER_HOME="/home/abc"
mkdir -p "$CODE_USER_HOME"
cat > "$CODE_USER_HOME/.bashrc" << 'EOL'
# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# User specific environment
if ! [[ "$PATH" =~ "$HOME/.local/bin:" ]]; then
    PATH="$HOME/.local/bin:$PATH"
fi

# Add virtual environment to PATH
if [ -d "$HOME/venv/bin" ]; then
    export PATH="$HOME/venv/bin:$PATH"
    source "$HOME/venv/bin/activate"
fi

export PATH
EOL
chown -R abc:abc "$CODE_USER_HOME/.bashrc"

echo "✅ Custom initialization completed successfully"
