from abc import ABC, abstractmethod
from argparse import Namespace
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.document import ResumeDocument, CoverLetterDocument
from factory import Factory


class IDocumentGenerator(ABC):
    """Interface for document generators."""
    
    @abstractmethod
    def generate(self, args: Namespace) -> Dict[str, Any]:
        """Generate document files.
        
        Args:
            args: Command-line arguments
            
        Returns:
            dict: Paths to generated files and other results
        """
        pass


class DocumentGenerator(IDocumentGenerator):
    """Base class for document generators."""
    
    def __init__(self, factory: Factory):
        """Initialize the document generator with the factory.
        
        Args:
            factory: Factory instance that provides access to all services
        """
        self.factory = factory
        self.renderer = factory.get_service('template_renderer')
        self.pdf_service = factory.get_service('pdf_service')
        self.html_service = factory.get_service('html_service')
        self.file_service = factory.get_service('file_service')
        self.config_manager = factory.get_service('config_manager')
        
    def _load_config(self) -> Dict[str, Any]:
        """Load content configuration using config manager.
        
        Returns:
            dict: Loaded configuration
        """
        # Get content path from factory app_config
        content_arg = self.factory.app_config.get('cli', {}).get('content_path_arg', 'content')
        # Get the actual path value from args (stored in factory)
        content_path = self.factory.args.get(content_arg, 'resume.toml')
        return self.config_manager.load(content_path)
    
    def _get_output_dir(self) -> Path:
        """Create and return the output directory for generated files.
        
        Returns:
            Path: Output directory path
        """
        return self.file_service.ensure_directory('output')
        
    def _get_name_prefix(self, config: Dict[str, Any]) -> tuple[str, str]:
        """Get formatted name prefix for filenames.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            tuple: (name_prefix, person_name)
        """
        person_name = config.get('personal', {}).get('name', '')
        name_prefix = self.document.format_name_for_filename(person_name)
        if name_prefix:
            name_prefix += "_"
        return name_prefix, person_name


class ResumeGenerator(DocumentGenerator):
    """Resume document generator."""
    
    def __init__(self, factory: Factory):
        """Initialize with factory."""
        super().__init__(factory)
        self.document = ResumeDocument()
    
    def generate(self, args: Namespace) -> Dict[str, Any]:
        """Generate resume HTML and PDF files.
        
        Args:
            args: Command-line arguments
            
        Returns:
            dict: Paths to generated files
        """
        # Announce generation start
        print("\nGenerating Resume document(s)")
        
        # Load config from factory
        config = self._load_config()
        
        # Get output directory
        output_dir = self._get_output_dir()
        
        # Determine whether to generate HTML from args
        generate_html = getattr(args, 'html', False)
        
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
        html_paths: List[Path] = []
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
    
    def __init__(self, factory: Factory):
        """Initialize with factory."""
        super().__init__(factory)
        self.document = CoverLetterDocument()
        
    def generate(self, args: Namespace) -> Dict[str, Any]:
        """Generate cover letter HTML and PDF files.
        
        Args:
            args: Command-line arguments
            
        Returns:
            dict: Paths to generated files
        """
        # Announce generation start
        print("\nGenerating Cover Letter document(s)")
        
        # Load config from factory
        config = self._load_config()
        
        # Get output directory
        output_dir = self._get_output_dir()
        
        # Determine whether to generate HTML from args
        generate_html = getattr(args, 'html', False)
        
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
        html_path: Optional[Path] = None
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
