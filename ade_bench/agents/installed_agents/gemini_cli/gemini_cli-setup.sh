#!/bin/bash
echo "Setup Gemini CLI"
apt-get update
apt-get install -y curl

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.2/install.sh | bash
source "$HOME/.nvm/nvm.sh"
nvm install 22
npm -v

echo "installing Gemini CLI"

npm install -g @google/gemini-cli

gemini --version

echo "Installed Gemini CLI"
