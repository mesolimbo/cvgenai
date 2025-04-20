#!/bin/bash
export PYTHONPATH=cvgenai:$PYTHONPATH

# Run the resume generator through pipenv using the simple entry point
pipenv run python cvgenai/cli.py "$@"
