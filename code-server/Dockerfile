FROM lscr.io/linuxserver/code-server:latest

# Install Python, Docker CLI, and ML dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
ENV VIRTUAL_ENV=/config/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python packages with pinned versions
# First install setuptools and wheel which are needed for building packages
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements file
COPY requirements.txt /tmp/requirements.txt

# Install the rest of the packages from requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Create workspace directory
WORKDIR /config/workspace

# Create extensions directory
RUN mkdir -p /config/.local/share/code-server/extensions

# Copy custom initialization scripts
COPY custom-cont-init.d/install-extensions.sh /etc/cont-init.d/99-install-extensions
RUN chmod +x /etc/cont-init.d/99-install-extensions

# Note: Extensions will be installed when the container starts via the custom init script
# LinuxServer.io's code-server image executes scripts in /etc/cont-init.d/ at startup