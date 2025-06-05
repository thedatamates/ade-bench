#!/bin/bash

apt-get update
apt-get install -y curl

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash

source "$HOME/.nvm/nvm.sh"

nvm install 22
npm -v
echo "installing claude code"
npm install -g @anthropic-ai/claude-code
echo "claude code installed"
dbt deps