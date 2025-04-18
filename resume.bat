@echo off
REM Resume generation script for Windows

REM Run the resume generator through pipenv
pipenv run python -m cvgenai.resume.generate %*
