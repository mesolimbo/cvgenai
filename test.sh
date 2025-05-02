#!/bin/bash

# Exit on error
set -e

# Display commands as they are executed
set -x

# Install the package in development mode
pipenv install -e .

# Run pytest with coverage and all arguments passed to this script
pipenv run pytest --cov=cvgenai --cov-report=term --cov-report=html "$@"