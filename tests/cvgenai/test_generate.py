"""Tests for the generate module."""

from unittest.mock import MagicMock
from pathlib import Path
from typing import Dict, List, Any

from cvgenai.generate import (
    DocumentGenerator,
    ResumeGenerator,
    CoverLetterGenerator
)
from cvgenai.document import ResumeDocument, CoverLetterDocument


def setup_document(document: Any):
    document.mock_config_manager = MagicMock()
    document.mock_factory = MagicMock()
    document.mock_renderer = MagicMock()
    document.mock_pdf_service = MagicMock()
    document.mock_html_service = MagicMock()
    document.mock_file_service = MagicMock()

    # Configure factory to return mocked services
    document.mock_factory.get_service.side_effect = lambda service_name: {
        'template_renderer': document.mock_renderer,
        'pdf_service': document.mock_pdf_service,
        'html_service': document.mock_html_service,
        'file_service': document.mock_file_service,
        'config_manager': document.mock_config_manager
    }[service_name]


class TestDocumentGenerator:
    """Test cases for the DocumentGenerator base class."""

    # Define class attributes with type annotations
    mock_factory = None
    mock_renderer = None
    mock_pdf_service = None
    mock_html_service = None
    mock_file_service = None
    mock_config_manager = None
    generator = None

    def setup_method(self):
        """Set up test fixtures before each test method."""
        setup_document(self)

        # Mock app_config and args in factory
        self.mock_factory.app_config = {'cli': {'content_path_arg': 'content'}}
        self.mock_factory.args = {'content': 'test_resume.toml'}
        
        # Create a test subclass that implements the abstract methods
        class TestDocGen(DocumentGenerator):
            def __init__(self, factory):
                super().__init__(factory)
                self.document = MagicMock()
                self.document_type = "test"

            @staticmethod
            def generate_output_files(elements: Dict[str, Any], context: Dict[str, Any], template_names: List[str],
                                      **kwargs):
                return {
                    'html_path': Path('test.html'),
                    'pdf_path': Path('test.pdf'),
                    'css_path': Path('test.css')
                }
        
        # Instantiate the test class
        self.generator = TestDocGen(self.mock_factory)

        # Mock format_name_for_filename to return a simple transformation
        self.generator.document.format_name_for_filename.side_effect = lambda x: x.replace(' ', '_').lower()

    def test_initialization(self):
        """Test the initialization process."""
        assert self.generator.factory == self.mock_factory
        assert self.generator.renderer == self.mock_renderer
        assert self.generator.pdf_service == self.mock_pdf_service
        assert self.generator.html_service == self.mock_html_service
        assert self.generator.file_service == self.mock_file_service
        assert self.generator.document_type == "test"

    def test_get_output_dir(self):
        """Test getting the output directory."""
        # Set up file service to return a path
        output_path = Path('output')
        self.mock_file_service.ensure_directory.return_value = output_path
        
        # Call the method
        result = self.generator._get_output_dir()
        
        # Verify the result
        assert result == output_path
        self.mock_file_service.ensure_directory.assert_called_once_with('output')

    def test_get_name_prefix(self):
        """Test getting the name prefix."""
        # Create a test config
        config = {'personal': {'name': 'Test User'}}

        # Call the method
        name_prefix, person_name = self.generator._get_name_prefix(config)
        
        # Verify the result
        assert person_name == 'Test User'
        assert name_prefix == 'test_user_'
        self.generator.document.format_name_for_filename.assert_called_once_with('Test User')

    def test_get_name_prefix_with_job(self):
        """Test name prefix when a job file is provided."""
        config = {'personal': {'name': 'Test User'}}

        # Add job argument to factory args
        self.mock_factory.args['job'] = 'jobs/example_job.txt'

        name_prefix, _ = self.generator._get_name_prefix(config)

        assert name_prefix == 'test_user_example_job_'

    def test_prepare_generation(self):
        """Test preparing generation elements."""
        # Mock necessary methods
        self.mock_file_service.ensure_directory.return_value = Path('output')
        
        # Create a mock Career instance
        mock_career = MagicMock()
        mock_career.get_data.return_value = {'personal': {'name': 'Test User'}}
        
        self.mock_file_service.copy_css.return_value = Path('output/style.css')
        
        # Create test args
        args = {'html': True}
        
        # Call the actual prepare_generation method
        result = self.generator.prepare_generation(args, mock_career)
        
        # Verify the method calls and result
        self.mock_file_service.ensure_directory.assert_called_once_with('output')
        self.mock_file_service.copy_css.assert_called_once_with('templates/style.css', Path('output'), True)
        mock_career.get_data.assert_called_once()

        # Verify the result structure and content
        assert 'config' in result
        assert result['output_dir'] == Path('output')
        assert result['generate_html'] is True
        assert result['name_prefix'] == 'test_user_'
        assert result['css_path'] == Path('output/style.css')

    def test_prepare_generation_with_job(self):
        """Prepare generation elements when job file is provided."""
        self.mock_file_service.ensure_directory.return_value = Path('output')

        mock_career = MagicMock()
        mock_career.get_data.return_value = {'personal': {'name': 'Test User'}}

        self.mock_file_service.copy_css.return_value = Path('output/style.css')

        args = {'html': False}

        self.mock_factory.args['job'] = 'jobs/example_job.txt'

        result = self.generator.prepare_generation(args, mock_career)

        assert result['name_prefix'] == 'test_user_example_job_'

    def test_generate_with_html(self):
        """Test generating documents with HTML option enabled."""
        # Mock document methods
        mock_context = {'name': 'Test User'}
        self.generator.document.prepare_context.return_value = mock_context
        self.generator.document.get_template_names.return_value = ['test_template.html']
        
        # Create a mock Career instance
        mock_career = MagicMock()
        mock_career.get_data.return_value = {'personal': {'name': 'Test User'}}
        
        # Create test args
        args = {'html': True}
        
        # Call the method
        result = self.generator.generate(args, mock_career)
        
        # Verify results
        assert result['html_path'] == Path('test.html')
        assert result['pdf_path'] == Path('test.pdf')
        assert result['css_path'] == Path('test.css')
        
        # Verify the document methods were called
        self.generator.document.prepare_context.assert_called_once()
        self.generator.document.get_template_names.assert_called_once()


class TestResumeGenerator:
    """Test cases for the ResumeGenerator class."""
    
    # Define class attributes with type annotations
    mock_factory = None
    mock_renderer = None
    mock_pdf_service = None
    mock_html_service = None
    mock_file_service = None
    generator = None

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create mock factory and services
        setup_document(self)

        # Create the generator
        self.generator = ResumeGenerator(self.mock_factory)

    def test_initialization(self):
        """Test the initialization of ResumeGenerator."""
        assert isinstance(self.generator.document, ResumeDocument)
        assert self.generator.document_type == "resume"

    def test_generate_output_files_with_html(self):
        """Test generating output files with HTML enabled."""
        # Setup test data
        elements = {
            'output_dir': Path('output'),
            'generate_html': True,
            'name_prefix': 'test_user_',
            'person_name': 'Test User',
            'css_path': Path('output/style.css')
        }
        context = {'name': 'Test User'}
        template_names = ['resume_page1_template.html', 'resume_page2_template.html']

        # Mock renderer to return HTML content
        self.mock_renderer.render.side_effect = [
            '<html><body>Page 1</body></html>',
            '<html><body>Page 2</body></html>'
        ]

        # Load elements into the generator
        self.generator.load_elements(elements)

        # Call the method
        result = self.generator.generate_output_files(elements, context, template_names)

        # Verify HTML service calls
        assert self.mock_html_service.save_html.call_count == 2

        # Verify PDF service call
        self.mock_pdf_service.generate_pdf_from_multiple_html.assert_called_once()

        # Verify the result structure
        assert 'html_paths' in result
        assert 'pdf_paths' in result
        assert 'css_path' in result
        assert len(result['html_paths']) == 2
        assert len(result['pdf_paths']) == 1


    def test_generate_output_files_without_html(self):
        """Test generating output files without HTML."""
        # Setup test data
        elements = {
            'output_dir': Path('output'),
            'generate_html': False,
            'name_prefix': 'test_user_',
            'person_name': 'Test User',
            'css_path': None
        }
        context = {'name': 'Test User'}
        template_names = ['resume_page1_template.html', 'resume_page2_template.html']
        
        # Mock renderer to return HTML content
        self.mock_renderer.render.side_effect = [
            '<html><body>Page 1</body></html>',
            '<html><body>Page 2</body></html>'
        ]

        # Load elements into the generator
        self.generator.load_elements(elements)
        
        # Call the method
        result = self.generator.generate_output_files(elements, context, template_names)
        
        # Verify HTML service was not called
        self.mock_html_service.save_html.assert_not_called()
        
        # Verify PDF service was called
        self.mock_pdf_service.generate_pdf_from_multiple_html.assert_called_once()
        
        # Verify the result structure
        assert 'html_paths' in result
        assert len(result['html_paths']) == 0  # No HTML files
        assert 'pdf_paths' in result
        assert len(result['pdf_paths']) == 1


class TestCoverLetterGenerator:
    """Test cases for the CoverLetterGenerator class."""
    
    # Define class attributes with type annotations
    mock_factory = None
    mock_renderer = None
    mock_pdf_service = None
    mock_html_service = None
    mock_file_service = None
    generator = None

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create mock factory and services
        setup_document(self)
        
        # Create the generator
        self.generator = CoverLetterGenerator(self.mock_factory)
        
    def test_initialization(self):
        """Test the initialization of CoverLetterGenerator."""
        assert isinstance(self.generator.document, CoverLetterDocument)
        assert self.generator.document_type == "cover_letter"
    
    def test_generate_output_files_with_html(self):
        """Test generating output files with HTML enabled."""
        # Setup test data
        elements = {
            'output_dir': Path('output'),
            'generate_html': True,
            'name_prefix': 'test_user_',
            'person_name': 'Test User',
            'css_path': Path('output/style.css')
        }
        context = {'name': 'Test User'}
        template_names = ['cover_letter_template.html']
        
        # Mock renderer to return HTML content
        self.mock_renderer.render.return_value = '<html><body>Cover Letter</body></html>'

        # Load elements into the generator
        self.generator.load_elements(elements)
        
        # Call the method
        result = self.generator.generate_output_files(elements, context, template_names)
        
        # Verify HTML service call
        self.mock_html_service.save_html.assert_called_once()
        
        # Verify PDF service call
        self.mock_pdf_service.generate_pdf_from_multiple_html.assert_called_once()
        
        # Verify the result structure
        assert 'html_paths' in result
        assert 'pdf_paths' in result
        assert 'css_path' in result


    def test_generate_output_files_without_html(self):
        """Test generating output files without HTML."""
        # Setup test data
        elements = {
            'output_dir': Path('output'),
            'generate_html': False,
            'name_prefix': 'test_user_',
            'person_name': 'Test User',
            'css_path': None
        }
        context = {'name': 'Test User'}
        template_names = ['cover_letter_template.html']
        
        # Mock renderer to return HTML content
        self.mock_renderer.render.return_value = '<html><body>Cover Letter</body></html>'

        # Load elements into the generator
        self.generator.load_elements(elements)
        
        # Call the method
        result = self.generator.generate_output_files(elements, context, template_names)
        
        # Verify HTML service was not called
        self.mock_html_service.save_html.assert_not_called()
        
        # Verify PDF service was called
        self.mock_pdf_service.generate_pdf_from_multiple_html.assert_called_once()
        
        # Verify the result structure
        assert result['html_paths'] == []  # No HTML file
        assert 'pdf_paths' in result

