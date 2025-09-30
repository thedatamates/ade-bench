#!/bin/bash
echo "Setup Macro"
apt-get update
apt-get install -y curl unixodbc unixodbc-dev

set -e

echo "installing Macro"

curl -LsSf https://getmacro.com/terminal/install.sh | bash
echo 'export PATH="$HOME/.macro/local:$PATH"' >> ~/.bashrc
source ~/.bashrc

macro --version

echo "Installed Macro"
