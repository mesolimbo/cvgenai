from core.document import ResumeDocument, CoverLetterDocument


class DocumentGenerator:
    """Base class for document generators."""
    
    def __init__(self, document, renderer, pdf_service, html_service, file_service):
        """Initialize the document generator with dependencies.
        
        Args:
            document: Document object that provides the context and templates
            renderer: Template renderer service
            pdf_service: PDF generation service
            html_service: HTML handling service
            file_service: File operations service
        """
        self.document = document
        self.renderer = renderer
        self.pdf_service = pdf_service
        self.html_service = html_service
        self.file_service = file_service
        
    def _get_name_prefix(self, config):
        """Get formatted name prefix for filenames."""
        person_name = config.get('personal', {}).get('name', '')
        name_prefix = self.document.format_name_for_filename(person_name)
        if name_prefix:
            name_prefix += "_"
        return name_prefix, person_name


class ResumeGenerator(DocumentGenerator):
    """Resume document generator."""
    
    def __init__(self, renderer, pdf_service, html_service, file_service):
        """Initialize with dependencies."""
        super().__init__(ResumeDocument(), renderer, pdf_service, html_service, file_service)
    
    def generate(self, config, output_dir, generate_html=False):
        """Generate resume HTML and PDF files.
        
        Args:
            config: Configuration dictionary
            output_dir: Output directory path
            generate_html: Whether to generate HTML files
            
        Returns:
            dict: Paths to generated files
        """
        # Prepare for file generation
        name_prefix, person_name = self._get_name_prefix(config)
        css_path = None
        if generate_html:
            css_path = self.file_service.copy_css('templates/style.css', output_dir)
        
        # Get context and template names
        context = self.document.prepare_context(config)
        template_names = self.document.get_template_names()
        
        # Render HTML content
        html_contents = [
            self.renderer.render(template_name, context)
            for template_name in template_names
        ]
        
        # Save HTML files if requested
        html_paths = []
        if generate_html:
            for i, html_content in enumerate(html_contents):
                html_path = output_dir / f'{name_prefix}resume_page{i+1}.html'
                self.html_service.save_html(html_content, str(html_path))  # Convert Path to string
                html_paths.append(html_path)
                print(f"   - HTML Page {i+1}: {html_path}")
        
        # Generate combined PDF
        pdf_path = output_dir / f'{name_prefix}resume.pdf'
        self.pdf_service.generate_pdf_from_multiple_html(html_contents, str(pdf_path))  # Convert Path to string
        
        # Print confirmation
        print(f"✅ Resume files generated for {person_name}:")
        if generate_html:
            if css_path:
                print(f"   - CSS: {css_path}")
        print(f"   - PDF: {pdf_path}")
        
        return {
            'html_paths': html_paths if generate_html else [],
            'pdf_paths': [pdf_path],
            'css_path': css_path
        }


class CoverLetterGenerator(DocumentGenerator):
    """Cover letter document generator."""
    
    def __init__(self, renderer, pdf_service, html_service, file_service):
        """Initialize with dependencies."""
        super().__init__(CoverLetterDocument(), renderer, pdf_service, html_service, file_service)
        
    def generate(self, config, output_dir, generate_html=False):
        """Generate cover letter HTML and PDF files.
        
        Args:
            config: Configuration dictionary
            output_dir: Output directory path
            generate_html: Whether to generate HTML files
            
        Returns:
            dict: Paths to generated files
        """
        # Prepare for file generation
        name_prefix, person_name = self._get_name_prefix(config)
        css_path = None
        if generate_html:
            css_path = self.file_service.copy_css('templates/style.css', output_dir)
        
        # Get context and template name
        context = self.document.prepare_context(config)
        template_name = self.document.get_template_names()[0]  # Cover letter has only one template
        
        # Render HTML content
        html_content = self.renderer.render(template_name, context)
        
        # Save HTML file if requested
        html_path = None
        if generate_html:
            html_path = output_dir / f'{name_prefix}cover_letter.html'
            self.html_service.save_html(html_content, str(html_path))  # Convert Path to string
            print(f"   - HTML: {html_path}")
        
        # Generate PDF
        pdf_path = output_dir / f'{name_prefix}cover_letter.pdf'
        self.pdf_service.generate_pdf(html_content, str(pdf_path))  # Convert Path to string
        
        # Print confirmation
        print(f"✅ Cover letter files generated for {person_name}:")
        if generate_html and css_path:
            print(f"   - CSS: {css_path}")
        print(f"   - PDF: {pdf_path}")
        
        return {
            'html_path': html_path,
            'pdf_path': pdf_path,
            'css_path': css_path
        }
