# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CVgenAI is a Python-based tool for generating professional resumes and cover letters in PDF and HTML formats. When an `OPENAI_API_KEY` environment variable is present, the tool can automatically tailor resume content to specific job descriptions using OpenAI's API (GPT-5.1). Without the key, it renders the provided content without customization.

## Essential Commands

### Running the Application
```bash
# Generate both resume and cover letter (PDF only)
./run.sh

# Generate only resume
./run.sh --resume

# Generate only cover letter
./run.sh --cover-letter

# Generate with HTML versions
./run.sh --html

# Customize for a specific job
./run.sh --job example_job.txt

# Use alternate content file
./run.sh --content my-other-resume.toml
```

### Development & Testing
```bash
# Install dependencies
pipenv install --dev

# Run all tests with coverage
./test.sh

# Run tests only (skip package installation)
./test.sh -t

# Run specific test file
pipenv run pytest tests/cvgenai/test_controller.py

# Run linting
pipenv run pylint src/cvgenai
```

### Important Notes
- Always use `pipenv run` to execute Python commands
- The `PYTHONPATH` must include the `src` directory (handled by `run.sh`)
- Import from `cvgenai` package directly (e.g., `from cvgenai.controller import CVGenController`)
- Do NOT include `src` in import paths
- Do NOT use relative imports

## Architecture Overview

This project follows SOLID principles with a configuration-driven factory pattern.

### Core Flow
1. **CLI** (`cli.py`) → Entry point that instantiates the controller
2. **Controller** (`controller.py`) → Orchestrates the generation workflow
3. **Factory** (`factory.py`) → Creates services and generators based on `app_config.toml`
4. **Generators** (`generate.py`) → Document-specific generation logic (Resume, CoverLetter)
5. **Services** (`services/`) → Modular services for HTML, PDF, file operations, and AI customization

### Key Components

#### Factory Pattern (`factory.py`)
- Dynamically loads service implementations from `app_config.toml`
- Creates document generators based on configuration
- Manages CLI argument parsing from config
- Uses dependency injection to provide services to generators

#### Services Architecture
- **ConfigManager** (`config.py`) - Loads TOML configuration files
- **Jinja2Renderer** (`templating/renderer.py`) - Template rendering
- **PDFService** (`services/pdf_service.py`) - PDF generation using WeasyPrint
- **HTMLService** (`services/html_service.py`) - HTML file operations
- **FileService** (`services/file_service.py`) - Safe file operations with project root validation
- **CustomizerService** (`services/customizer_service.py`) - AI-powered content customization using OpenAI Responses API

#### Document Abstraction (`document.py`)
- Base `Document` class defines interface for all document types
- `ResumeDocument` - Handles two-page resume layout and context preparation
- `CoverLetterDocument` - Handles single-page cover letter formatting
- Each document type knows its own template names and context structure

#### Career Data Model (`career.py`)
- Loads and stores resume content from TOML files
- Optionally applies AI customization via lambda function
- Provides unified interface for accessing career data

### AI Customization Flow
1. User provides `--job path/to/job.txt` argument
2. Factory reads job description via FileService (with safety checks)
3. CustomizerService uses OpenAI's Responses API with GPT-5.1
4. AI rewrites TOML content to emphasize relevant skills while maintaining structure
5. Career model loads the customized TOML
6. Generators use customized content for rendering

### Configuration System

#### `app_config.toml`
Defines the entire application structure:
- Service implementations (allows swapping implementations without code changes)
- CLI arguments (dynamically generates argument parser)
- Document generators (order, enabled/disabled state, CLI flags)

#### `resume.toml`
User-provided content including:
- Personal information
- Resume sections (summary, career highlights, experience, education)
- Cover letter content (recipient, body)
- Skills reference (used by AI for better customization)

### Adding New Features

#### Add a new document type:
1. Create a new `Document` subclass in `document.py`
2. Create a new generator class extending `DocumentGenerator` in `generate.py`
3. Add configuration to `app_config.toml` under `[[documents.generators]]`
4. Create corresponding Jinja2 template(s) in `templates/`

#### Add a new service:
1. Implement the service class with appropriate interface
2. Register in `app_config.toml` under `[services]`
3. Access via `factory.get_service('service_name')`

#### Modify AI customization:
- Update `CustomizerService` in `services/customizer_service.py`
- The service uses OpenAI Responses API with system instructions
- Instructions enforce TOML format preservation and layout restrictions

## File Structure Notes

- **Templates** (`templates/`) - Jinja2 HTML templates with `style.css`
- **Output** (`output/`) - Generated files: `[name]_[job]_resume.pdf`, `[name]_[job]_cover_letter.pdf`
- **Tests** (`tests/`) - pytest suite (NOT packages, just modules)
- **Source** (`src/cvgenai/`) - Main package code

## Development Context

- Python 3.12+ required
- Use pipenv for all dependency management
- Git bash is the default terminal on Windows
- Tests use pytest with coverage reporting
- Sparse type hints used only for clarification
- Docstrings follow Google/NumPy style
- The project is intentionally kept simple - avoid over-engineering abstractions
