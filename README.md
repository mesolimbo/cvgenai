# CV Generator AI

A tool for generating professional resumes and cover letters in PDF and HTML formats.

## Features

- Generate professional resumes with a consistent, two-page layout
- Generate matching cover letters
- Produce both PDF and HTML output formats
- Customize content via TOML configuration
- Support for multiple profiles/people

## Installation

### Prerequisites

- Python 3.8+
- [Pipenv](https://pipenv.pypa.io/) for dependency management

### Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd cvgenai
   ```

2. Install dependencies with pipenv:
   ```bash
   pipenv install
   ```

3. Create your configuration:
   ```bash
   cp config-sample.toml config.toml
   ```

4. Edit the `config.toml` file with your personal information, work experience, and other details.

## Usage

### Basic Usage

Generate both resume and cover letter (PDF only):

**Windows**:
```
resume.bat
```

**Unix/Linux/Mac**:
```
./resume.sh
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--resume` | Generate only the resume |
| `--cover-letter` | Generate only the cover letter |
| `--html` | Generate HTML versions in addition to PDFs |
| `--config PATH` | Specify an alternative config file (default: `config.toml`) |

### Examples

Generate only the resume:
```
resume.bat --resume
```

Generate both resume and cover letter with HTML versions:
```
resume.bat --resume --cover-letter --html
```

Use a specific configuration file:
```
resume.bat --config my-other-config.toml
```

## Project Structure

- **`config.toml`**: Your personal resume and cover letter information
- **`cvgenai/`**: Main package
  - **`run.py`**: Main entry point and CLI functionality
  - **`config/`**: Configuration handling
    - **`toml.py`**: TOML configuration loading
  - **`resume/`**: Resume and cover letter generation 
    - **`generate.py`**: Document generation functions
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
    - `style.css`: Copy of the CSS file

## Customization

### Templates

You can modify the templates in the `templates/` directory to customize the appearance of your resume and cover letter. The templates use Jinja2 syntax.

### Styles

Edit the `templates/style.css` file to customize the styling of your documents.

### Configuration

The `config.toml` file contains all the content for your resume and cover letter. You can create multiple configuration files for different job applications or different people.

## Tips

- Keep each bullet point in your experience and education sections concise for better formatting
- Use the `--html` option during development to quickly preview changes in a web browser
- Create multiple config files for different job applications (e.g., `config-dev.toml`, `config-manager.toml`)
- For multiple people, use separate configuration files and specify with `--config`

## License

[Specify license information here]
