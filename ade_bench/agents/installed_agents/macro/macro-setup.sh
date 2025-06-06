#!/bin/bash
echo "setup macro"
apt-get update
apt-get install -y curl unixodbc unixodbc-dev

#!/bin/bash
set -e

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    ARCH_DIR="amd64"
elif [ "$ARCH" = "aarch64" ]; then
    ARCH_DIR="arm64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

echo "Detected architecture: $ARCH ($ARCH_DIR)"

# Download tdm binary from host machine based on architecture
# Assumes the host is running a simple HTTP server on port 8989
curl -L http://host.docker.internal:8989/target/docker/${ARCH_DIR}/tdm -o /usr/local/bin/macro

curl -L http://host.docker.internal:8989/tdm.test.toml -o tdm.toml

mkdir /var/log/macro-agent

# Make it executable
chmod +x /usr/local/bin/macro

echo "installed macro binary"