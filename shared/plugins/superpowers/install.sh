#!/bin/bash
set -e

echo "Installing superpowers for Claude Code..."

# Add superpowers marketplace
claude plugin marketplace add obra/superpowers-marketplace

# Install superpowers plugin
claude plugin install superpowers@superpowers-marketplace

echo "Superpowers installed successfully"
