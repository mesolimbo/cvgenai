from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from pathlib import Path
import shutil
import tomli

def load_config(config_path):
    """Load configuration from TOML file."""
    with open(config_path, 'rb') as f:
        return tomli.load(f)

def render_html(template_name, context):
    """Render HTML using Jinja2 template."""
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    return template.render(context)

def generate_pdf(html_string, output_path):
    """Generate PDF from HTML string using WeasyPrint."""
    HTML(string=html_string).write_pdf(
        output_path,
        stylesheets=[CSS('templates/style.css')]
    )

def generate_pdf_from_multiple_html(html_strings, output_path):
    """Generate a single PDF from multiple HTML strings using WeasyPrint."""
    from weasyprint import HTML, CSS
    html_objs = [HTML(string=html) for html in html_strings]
    # Use the first HTML as the base, append the rest as pages
    base_doc = html_objs[0].render(stylesheets=[CSS('templates/style.css')])
    for html_obj in html_objs[1:]:
        doc = html_obj.render(stylesheets=[CSS('templates/style.css')])
        base_doc.pages.extend(doc.pages)
    base_doc.write_pdf(output_path)

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

def split_intro_and_bullets(text, require_intro=True):
    """Split a block of text into an intro and a list of bullet points.
    If require_intro is False, treat all lines as bullets."""
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    if not lines:
        return ('', []) if require_intro else []
    if require_intro:
        intro = lines[0]
        bullets = []
        for line in lines[1:]:
            if line.startswith('- '):
                bullets.append(line[2:].strip())
            elif line.startswith('• '):
                bullets.append(line[2:].strip())
            else:
                bullets.append(line)
        return intro, bullets
    else:
        bullets = []
        for line in lines:
            if line.startswith('- '):
                bullets.append(line[2:].strip())
            elif line.startswith('• '):
                bullets.append(line[2:].strip())
            else:
                bullets.append(line)
        return bullets

def main():
    # Load configuration
    config = load_config('config.toml')

    # Create output directory if it doesn't exist
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)

    # Copy CSS file to output directory
    css_path = copy_css(output_dir)

    # Prepare context for both pages
    resume = config.get('resume', {})
    summary_intro, summary_bullets = split_intro_and_bullets(resume.get('summary', ''), require_intro=True)
    highlights_bullets = split_intro_and_bullets(resume.get('career_highlights', ''), require_intro=False)
    context = {
        'personal': config.get('personal', {}),
        'resume': resume,
        'summary_intro': summary_intro,
        'summary_bullets': summary_bullets,
        'highlights_bullets': highlights_bullets,
    }

    # Render Page 1
    html_page1 = render_html('resume_page1_template.html', context)
    html_path1 = output_dir / 'resume_page1.html'
    save_html(html_page1, html_path1)

    # Render Page 2
    html_page2 = render_html('resume_page2_template.html', context)
    html_path2 = output_dir / 'resume_page2.html'
    save_html(html_page2, html_path2)

    # Generate a single PDF with both pages
    pdf_path = output_dir / 'resume.pdf'
    generate_pdf_from_multiple_html([html_page1, html_page2], pdf_path)

    print(f"✅ Resume files generated:")
    print(f"   - Page 1 HTML: {html_path1}")
    print(f"   - Page 2 HTML: {html_path2}")
    print(f"   - PDF (2 pages): {pdf_path}")
    print(f"   - CSS: {css_path}")

if __name__ == '__main__':
    main()
