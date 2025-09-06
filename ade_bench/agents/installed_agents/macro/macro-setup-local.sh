#!/bin/bash
echo "Setup Macro (Custom Binary)"
apt-get update
apt-get install -y curl unixodbc unixodbc-dev

# Check if custom macro binary was copied
if [ -f "/installed-agent/macro" ]; then
    echo "Using custom macro binary"
    # Make it executable and move to path
    chmod +x /installed-agent/macro
    mkdir -p $HOME/.macro/local
    mv /installed-agent/macro $HOME/.macro/local/
    echo 'export PATH="$HOME/.macro/local:$PATH"' >> ~/.bashrc
    source ~/.bashrc
else
    echo "ERROR: Custom binary not found, but MACRO_BINARY_PATH was set"
    exit 1
fi

macro --version
echo "Installed Macro Terminal"
