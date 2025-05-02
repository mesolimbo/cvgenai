"""PDF generation service for CV Generation."""

from weasyprint import HTML, CSS


class PDFService:
    """Service for generating PDF documents."""
    
    def __init__(self, css_path='templates/style.css'):
        """Initialize with CSS path for styling."""
        self.css_path = css_path
    
    def generate_pdf(self, html_content, output_path):
        """Generate PDF from HTML string using WeasyPrint."""
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[CSS(self.css_path)]
        )
    
    def generate_pdf_from_multiple_html(self, html_contents, output_path):
        """Generate a single PDF from multiple HTML strings using WeasyPrint."""
        html_objs = [HTML(string=html) for html in html_contents]
        # Use the first HTML as the base, append the rest as pages
        base_doc = html_objs[0].render(stylesheets=[CSS(self.css_path)])
        for html_obj in html_objs[1:]:
            doc = html_obj.render(stylesheets=[CSS(self.css_path)])
            base_doc.pages.extend(doc.pages)
        base_doc.write_pdf(output_path)
