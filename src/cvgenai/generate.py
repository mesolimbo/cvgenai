from abc import ABC, abstractmethod
from argparse import Namespace
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from cvgenai.document import ResumeDocument, CoverLetterDocument
from cvgenai.factory import Factory

# Factory module interface for creating service and generator instances based on configuration
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
        raise NotImplementedError("Subclasses must implement this method")


# Reference implementation of the document generator interface
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
        self.document = None  # To be set by subclasses
        self.document_type = "document"  # To be overridden by subclasses
        self.output_dir = None
        self.generate_html = None
        self.name_prefix = None
        self.person_name = None
        self.css_path = None
    

    def load_elements(self, elements: Dict[str, Any]):
        """Load common elements for document generation."""
        self.output_dir = elements['output_dir']
        self.generate_html = elements['generate_html']
        self.name_prefix = elements['name_prefix']
        self.person_name = elements['person_name']
        self.css_path = elements['css_path']


    def generate(self, args: Namespace) -> Dict[str, Any]:
        """Generate document files.
        
        Args:
            args: Command-line arguments
            
        Returns:
            dict: Paths to generated files and other results
        """
        # Announce generation start
        print(f"\nGenerating {self.document_type.title()} document(s)")
        
        # Prepare common elements
        elements = self.prepare_generation(args)
        self.load_elements(elements)
        
        # Get context and template names
        context = self.document.prepare_context(elements['config'])
        template_names = self.document.get_template_names()
        
        # Generate HTML and PDF
        return self.generate_output_files(elements, context, template_names)


    def prepare_generation(self, args: Namespace) -> Dict[str, Any]:
        """Prepare common elements for document generation.

        Args:
            args: Command-line arguments

        Returns:
            dict: Common elements needed for generation
        """
        # Load config
        config = self._load_config()

        # Get output directory
        output_dir = self._get_output_dir()

        # Determine whether to generate HTML from args
        generate_html = getattr(args, 'html', False)

        # Get name prefix for files
        name_prefix, person_name = self._get_name_prefix(config)

        # Copy CSS only if generating HTML
        css_path = self.file_service.copy_css('templates/style.css', output_dir, generate_html)

        return {
            'config': config,
            'output_dir': output_dir,
            'generate_html': generate_html,
            'name_prefix': name_prefix,
            'person_name': person_name,
            'css_path': css_path
        }


    def generate_output_files(
            self,
            elements: Dict[str, Any],
            context: Dict[str, Any],
            template_names: List[str]
    ) -> Dict[str, Any]:
        """Generate HTML and PDF output files for document.

        Args:
            elements: Common elements from prepare_generation
            context: Template rendering context
            template_names: List of template names to render

        Returns:
            dict: Paths to generated files
        """
        # Render HTML content
        html_contents = [
            self.renderer.render(template_name, context)
            for template_name in template_names
        ]

        # Save HTML files if requested
        html_paths: List[Path] = []
        if self.generate_html:
            for i, html_content in enumerate(html_contents):
                html_path = self.output_dir / f'{self.name_prefix}{self.document_type}_page{i + 1}.html'
                self.html_service.save_html(html_content, str(html_path))
                html_paths.append(html_path)

        # Generate combined PDF
        pdf_path = self.output_dir / f'{self.name_prefix}{self.document_type}.pdf'
        self.pdf_service.generate_pdf_from_multiple_html(html_contents, str(pdf_path))

        # Print confirmation
        self._print_confirmation(self.person_name, self.generate_html, self.css_path, html_paths, pdf_path)

        return {
            'html_paths': html_paths if self.generate_html else [],
            'pdf_paths': [pdf_path],
            'css_path': self.css_path
        }


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


    def _get_name_prefix(self, config: Dict[str, Any]) -> Tuple[str, str]:
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


    def _print_confirmation(
        self,
        person_name: str, 
        generate_html: bool, 
        css_path: Optional[Path], 
        html_paths: Union[List[Path], Optional[Path]], 
        pdf_path: Path
    ) -> None:
        """Print confirmation of generated files.
        
        Args:
            person_name: Person's name from config
            generate_html: Whether HTML was generated
            css_path: Path to the CSS file if copied
            html_paths: Path(s) to HTML file(s)
            pdf_path: Path to the PDF file
        """
        print(f"✅ {self.document_type.title()} files generated for {person_name}:")
        if generate_html:
            if css_path:
                print(f"   - CSS: {css_path}")
            
            # Handle both single HTML path and list of paths
            if isinstance(html_paths, list):
                for i, path in enumerate(html_paths):
                    print(f"   - HTML Page {i+1}: {path}")
            elif html_paths:
                print(f"   - HTML: {html_paths}")
                
        print(f"   - PDF: {pdf_path}")


class ResumeGenerator(DocumentGenerator):
    """Resume document generator."""
    
    def __init__(self, factory: Factory):
        """Initialize with factory."""
        super().__init__(factory)
        self.document = ResumeDocument()
        self.document_type = "resume"


class CoverLetterGenerator(DocumentGenerator):
    """Cover letter document generator."""
    
    def __init__(self, factory: Factory):
        """Initialize with factory."""
        super().__init__(factory)
        self.document = CoverLetterDocument()
        self.document_type = "cover_letter"
