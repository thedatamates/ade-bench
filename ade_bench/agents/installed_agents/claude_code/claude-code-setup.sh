#!/bin/bash
echo "Setup Claude Code"
apt-get update
apt-get install -y curl

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
source "$HOME/.nvm/nvm.sh"
nvm install 22
npm -v

echo "installing Claude Code"

npm install -g @anthropic-ai/claude-code

claude --version

echo "Installed Claude Code"
