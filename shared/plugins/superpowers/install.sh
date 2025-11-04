#!/bin/bash
set -e

echo "Installing superpowers for Claude Code..."


# XXX: right now there's no post-agent-instaill hook, so we are just installing claude-code here
npm install -g @anthropic-ai/claude-code

# Add superpowers marketplace
claude plugin marketplace add obra/superpowers-marketplace

# Install superpowers plugin
claude plugin install superpowers@superpowers-marketplace

echo "Superpowers installed successfully"
