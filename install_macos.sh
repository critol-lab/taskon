#!/bin/zsh
set -euo pipefail
# macOS Apple Silicon setup for TaskOn
# 1) Install Homebrew if missing: https://brew.sh
# 2) brew install python@3.11 git
# 3) curl -sSL https://install.python-poetry.org | python3 -
# 4) export PATH="$HOME/Library/Python/3.11/bin:$HOME/.local/bin:$PATH"

# Create venv via Poetry and install deps
poetry install
