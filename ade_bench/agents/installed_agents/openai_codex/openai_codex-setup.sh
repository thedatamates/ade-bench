#!/bin/bash
echo "Setup OpenAI Codex"
apt-get update
apt-get install -y curl

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
source "$HOME/.nvm/nvm.sh"
nvm install 22
npm -v

echo "installing OpenAI Codex"

npm install -g @openai/codex

codex --version

echo "Installed OpenAI Codex"
