#!/bin/bash

# Exit on error
set -e

# Display commands as they are executed
set -x

# Default: don't skip install
SKIP_INSTALL=false

# Parse options
while getopts "t" opt; do
  case $opt in
    t)
      SKIP_INSTALL=true
      ;;
    *)
      echo "Usage: $0 [-t] [pytest_args]"
      echo "  -t: Skip installation step (test only)"
      exit 1
      ;;
  esac
done

# Remove processed options
shift $((OPTIND-1))

# Install the package in development mode (unless skipped)
if [ "$SKIP_INSTALL" = false ]; then
  pipenv install -e .
fi

# Run pytest with coverage and all arguments passed to this script
pipenv run pytest --cov=cvgenai --cov-report=term --cov-report=html "$@"
