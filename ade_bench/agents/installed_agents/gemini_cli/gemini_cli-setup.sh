#!/bin/bash
echo "Setup Gemini CLI"

# Node.js should already be pre-installed in the Docker image
node --version
npm --version

echo "installing Gemini CLI"

npm install -g @google/gemini-cli

gemini --version

echo "Installed Gemini CLI"
