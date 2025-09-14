#!/bin/zsh
set -euo pipefail
export PATH="$HOME/Library/Python/3.11/bin:$HOME/.local/bin:$PATH"
poetry run python main.py
