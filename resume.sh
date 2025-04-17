#!/bin/bash

# Run the resume generator through pipenv
pipenv run python -m src.resume.generate "$@"
