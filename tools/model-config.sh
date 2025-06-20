#!/bin/bash
# Model Configuration Tool for Linux/macOS
# Manages model configurations across substrate-based projects

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
python3 "$SCRIPT_DIR/model-config.py" "$@"
