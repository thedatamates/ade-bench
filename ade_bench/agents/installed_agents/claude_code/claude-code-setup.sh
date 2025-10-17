#!/bin/bash
echo "Setup Claude Code"

# Node.js should already be pre-installed in the Docker image
node --version
npm --version

echo "installing Claude Code"

npm install -g @anthropic-ai/claude-code

claude --version

echo "Installed Claude Code"
