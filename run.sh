#!/bin/bash
# Get the current directory in Unix-style path
CURRENT_DIR=$(pwd)

# Set the PYTHONPATH to include the src directory
export PYTHONPATH="$CURRENT_DIR/src"

# Run the resume generator through pipenv using the simple entry point
pipenv run python src/cvgenai/cli.py "$@"
