#!/bin/bash
echo "Setup Macro"
apt-get update
apt-get install -y curl unixodbc unixodbc-dev

#!/bin/bash
set -e

curl -LsSf https://getmacro.com/terminal/install.sh | bash
echo 'export PATH="$HOME/.macro/local:$PATH"' >> ~/.bashrc
source ~/.bashrc

macro --version

echo "Installed Macro Terminal"