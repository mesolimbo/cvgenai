from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from pathlib import Path
import shutil
import tomli

def load_config(config_path):
    """Load configuration from TOML file."""
    with open(config_path, 'rb') as f:
        return tomli.load(f)

def render_html(template_name, content, recipient, **kwargs):
    """Render HTML using Jinja2 template."""
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    
    # Split content by double newlines and wrap each paragraph in p tags
    paragraphs = content.strip().split('\n\n')
    html_content = '\n'.join(f'<p>{p.strip()}</p>' for p in paragraphs)
    
    context = {
        'content': html_content,
        'recipient': recipient
    }
    context.update(kwargs)
    return template.render(context)

def generate_pdf(html_string, output_path):
    """Generate PDF from HTML string using WeasyPrint."""
    HTML(string=html_string).write_pdf(
        output_path,
        stylesheets=[CSS('templates/style.css')]
    )

def save_html(html_string, output_path):
    """Save HTML string to a file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_string)

def copy_css(output_dir):
    """Copy the CSS file to the output directory."""
    css_source = Path('templates/style.css')
    css_dest = output_dir / 'style.css'
    shutil.copy2(css_source, css_dest)
    return css_dest

def main():
    # Load configuration
    config = load_config('config.toml')
    
    # Create output directory if it doesn't exist
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)

    # Copy CSS file to output directory
    css_path = copy_css(output_dir)

    # Render the HTML using config values
    html_content = render_html(
        'cover_letter_template.html',
        config['content']['cover_letter'],
        config['content']['recipient'],
        **config['personal']
    )

    # Save both HTML and PDF
    html_path = output_dir / 'cover_letter.html'
    pdf_path = output_dir / 'cover_letter.pdf'
    
    save_html(html_content, html_path)
    generate_pdf(html_content, pdf_path)
    
    print(f"✅ Files generated:")
    print(f"   - HTML: {html_path}")
    print(f"   - PDF: {pdf_path}")
    print(f"   - CSS: {css_path}")

if __name__ == '__main__':
    main() 
