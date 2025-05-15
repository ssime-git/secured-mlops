#!/bin/bash

# This script will run when the container starts
# It installs VS Code extensions for the code-server

echo "Installing VS Code extensions..."

# Make sure the extensions directory exists
mkdir -p /config/.local/share/code-server/extensions

# Install extensions
/app/code-server/bin/code-server --install-extension ms-python.python
/app/code-server/bin/code-server --install-extension ms-python.vscode-pylance
/app/code-server/bin/code-server --install-extension ms-toolsai.jupyter
/app/code-server/bin/code-server --install-extension njpwerner.autodocstring
/app/code-server/bin/code-server --install-extension ms-python.black-formatter
/app/code-server/bin/code-server --install-extension matangover.mypy

echo "VS Code extensions installed successfully"
