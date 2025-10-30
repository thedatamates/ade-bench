#!/bin/bash
echo "Setup OpenAI Codex"

# Node.js should already be pre-installed in the Docker image
node --version
npm --version

echo "installing OpenAI Codex"

npm install -g @openai/codex

codex --version

echo "Installed OpenAI Codex"
