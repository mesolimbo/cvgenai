# CV Generator AI

A tool for generating professional resumes and cover letters in PDF and HTML formats.

## Features

- Generate professional resumes with a consistent, two-page layout
- Generate matching cover letters
- Produce both PDF and HTML output formats
- Customize content via TOML resume document
- Support for multiple profiles/people

## Installation

### Prerequisites

- Python 3.8+
- [Pipenv](https://pipenv.pypa.io/) for dependency management

### Setup

1. Clone this repository

2. Install dependencies with pipenv:
   ```bash
   pipenv install --dev
   ```

3. Create your personal resume content document:
   ```bash
   cp resume-sample.toml resume.toml
   ```

4. Edit the `resume.toml` file with your personal information, work experience, and other resume details.

When running scripts or commands, ensure that the PYTHONPATH is set to include the `src` directory. This ensures that the `cvgenai` module can be correctly located and imported.

## Usage

### Basic Usage

Generate both resume and cover letter (PDF only):

```bash
./run.sh
```

### Running Tests

Run all tests (this will install the package first):

```bash
./test.sh
```

Skip the package installation and only run tests:

```bash
./test.sh -t
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--resume` | Generate only the resume |
| `--cover-letter` | Generate only the cover letter |
| `--html` | Generate HTML versions in addition to PDFs |
| `--content PATH` | Specify an alternative resume content file (default: `resume.toml`) |

### Examples

Generate only the resume:
```bash
run.sh --resume
```

Generate both resume and cover letter with HTML versions:
```bash
run.sh --resume --cover-letter --html
```

Use an alternate content file:
```bash
run.sh --content my-other-resume.toml
```

## Project Structure

![Class Diagram](diagrams/Classes%20-%20cvgenai.svg)
[Download PDF](diagrams/Classes%20-%20cvgenai.pdf)

- **`resume.toml`**: Your personal resume and cover letter information
- **`src/cvgenai/`**: Main package
  - **`cli.py`**: Command-line interface functionality
  - **`document.py`**: Document abstractions and implementations
  - **`factory.py`**: Creating service and generator instances based on configuration TOML
  - **`generate.py`**: Resume and cover letter document generation
  - **`config.py`**: TOML configuration loading via ConfigManager
  - **`services/`**: Independent service classes
    - **`file_service.py`**: File operations service
    - **`html_service.py`**: HTML generation service
    - **`pdf_service.py`**: PDF generation service
  - **`templating/`**: Template rendering
    - **`renderer.py`**: Template renderer interface and implementations
- **`templates/`**: Contains HTML templates and CSS styles
  - `cover_letter_template.html`: Template for cover letters
  - `resume_page1_template.html`: Template for resume page 1
  - `resume_page2_template.html`: Template for resume page 2
  - `style.css`: Styling for all documents
- **`output/`**: Where generated files are saved
  - `[name]_resume.pdf`: Complete resume (both pages combined)
  - `[name]_cover_letter.pdf`: Cover letter
  - When `--html` is used:
    - `[name]_resume_page1.html`: HTML for first page of the resume
    - `[name]_resume_page2.html`: HTML for second page of the resume
    - `[name]_cover_letter.html`: HTML version of the cover letter
    - `style.css`: Copy of the CSS file used

## Customization

### Templates

You can modify the templates in the `templates/` directory to customize the appearance of your resume and cover letter. The templates use Jinja2 syntax.

### Styles

Edit the `templates/style.css` file to customize the styling of your documents.

### Content

The `resume.toml` file contains all the content for your resume and cover letter. You can create multiple content files for different job applications, different roles, or different people.

## Extending the Project

Thanks to the SOLID architecture, you can easily extend the project:

1. **Add new document types**: Create a new class that extends the `Document` base class
2. **Add new output formats**: Create a new service class and implement the appropriate interface
3. **Change the templating engine**: Create a new class that implements the `ITemplateRenderer` interface

## Tips

- Keep each bullet point in your experience and education sections concise for better formatting
- Use the `--html` option during development to quickly preview changes in a web browser
- Create multiple content files for different job applications (e.g., `resume-dev.toml`, `resume-manager.toml`)
- For multiple people, use separate content files and specify with `--content`

## License

[Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)
