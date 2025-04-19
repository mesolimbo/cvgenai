from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from pathlib import Path
import shutil
import re

def render_html(template_name, context):
    """Render HTML using Jinja2 template."""
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    return template.render(context)

def render_cover_letter_html(template_name, content, recipient, **kwargs):
    """Render HTML using Jinja2 template for cover letter."""
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

def generate_pdf_from_multiple_html(html_strings, output_path):
    """Generate a single PDF from multiple HTML strings using WeasyPrint."""
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

def format_name_for_filename(name):
    """Convert a person's name to a filename-friendly format.
    Example: 'Jane Smith' becomes 'jane_smith'
    """
    # Replace spaces with underscores and make lowercase
    formatted_name = name.strip().lower().replace(' ', '_')
    # Remove any characters that aren't suitable for filenames
    formatted_name = re.sub(r'[^\w_]', '', formatted_name)
    return formatted_name

def copy_css(output_dir):
    """Copy the CSS file to the output directory."""
    css_source = Path('templates/style.css')
    css_dest = output_dir / 'style.css'
    shutil.copy2(css_source, css_dest)
    return css_dest

def generate_resume(config, output_dir, generate_html=False):
    """Generate resume HTML and PDF files."""
    # Copy CSS file to output directory only if HTML is enabled
    css_path = None
    if generate_html:
        css_path = copy_css(output_dir)
    
    # Get person's name for filenames
    person_name = config.get('personal', {}).get('name', '')
    name_prefix = format_name_for_filename(person_name)
    if name_prefix:
        name_prefix += "_"

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
    html_path1 = output_dir / f'{name_prefix}resume_page1.html'
    if generate_html:
        save_html(html_page1, html_path1)

    # Render Page 2
    html_page2 = render_html('resume_page2_template.html', context)
    html_path2 = output_dir / f'{name_prefix}resume_page2.html'
    if generate_html:
        save_html(html_page2, html_path2)

    # Generate a single PDF with both pages
    pdf_path = output_dir / f'{name_prefix}resume.pdf'
    generate_pdf_from_multiple_html([html_page1, html_page2], pdf_path)
    
    # We no longer generate individual page PDFs
    # page1_pdf = output_dir / f'{name_prefix}resume_page1.pdf'
    # page2_pdf = output_dir / f'{name_prefix}resume_page2.pdf'
    # generate_pdf(html_page1, page1_pdf)
    # generate_pdf(html_page2, page2_pdf)

    print(f"✅ Resume files generated for {person_name}:")
    if generate_html:
        print(f"   - Page 1 HTML: {html_path1}")
        print(f"   - Page 2 HTML: {html_path2}")
        print(f"   - CSS: {css_path}")
    print(f"   - PDF: {pdf_path}")
    
    return {
        'html_paths': [html_path1, html_path2] if generate_html else [],
        'pdf_paths': [pdf_path],
        'css_path': css_path if generate_html else None
    }

def generate_cover_letter(config, output_dir, generate_html=False):
    """Generate cover letter HTML and PDF files."""
    # Copy CSS file to output directory only if HTML is enabled
    css_path = None
    if generate_html:
        css_path = copy_css(output_dir)
    
    # Get person's name for filenames
    person_name = config.get('personal', {}).get('name', '')
    name_prefix = format_name_for_filename(person_name)
    if name_prefix:
        name_prefix += "_"

    # Render the HTML using config values
    html_content = render_cover_letter_html(
        'cover_letter_template.html',
        config['content']['cover_letter'],
        config['content']['recipient'],
        **config['personal']
    )

    # Save both HTML and PDF
    html_path = output_dir / f'{name_prefix}cover_letter.html'
    pdf_path = output_dir / f'{name_prefix}cover_letter.pdf'
    
    if generate_html:
        save_html(html_content, html_path)
    generate_pdf(html_content, pdf_path)
    
    print(f"✅ Cover letter files generated for {person_name}:")
    if generate_html:
        print(f"   - HTML: {html_path}")
        print(f"   - CSS: {css_path}")
    print(f"   - PDF: {pdf_path}")
    
    return {
        'html_path': html_path if generate_html else None,
        'pdf_path': pdf_path,
        'css_path': css_path if generate_html else None
    }
