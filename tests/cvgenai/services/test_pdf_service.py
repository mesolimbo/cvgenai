"""Tests for the pdf_service module."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from cvgenai.services.pdf_service import PDFService


class TestPDFService:
    """Test cases for the PDFService class."""

    def test_init_default_css_path(self):
        """Test initializing with default CSS path."""
        service = PDFService()
        assert service.css_path == 'templates/style.css'

    def test_init_custom_css_path(self):
        """Test initializing with custom CSS path."""
        custom_path = 'custom/path/style.css'
        service = PDFService(css_path=custom_path)
        assert service.css_path == custom_path

    @patch('cvgenai.services.pdf_service.HTML')
    @patch('cvgenai.services.pdf_service.CSS')
    def test_generate_pdf(self, mock_css, mock_html):
        """Test generating PDF from HTML content."""
        # Setup mocks
        mock_html_instance = MagicMock()
        mock_html.return_value = mock_html_instance
        
        # Create temp directory and file for output
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_output.pdf"
            
            # Test data
            html_content = "<html><body><h1>Test PDF</h1></body></html>"
            css_path = 'test/style.css'
            
            # Create service and generate PDF
            service = PDFService(css_path=css_path)
            service.generate_pdf(html_content, str(output_path))
            
            # Verify mocks were called correctly
            mock_html.assert_called_once_with(string=html_content)
            mock_html_instance.write_pdf.assert_called_once()
            mock_css.assert_called_once_with(css_path)

    @patch('cvgenai.services.pdf_service.CSS')
    def test_generate_pdf_from_multiple_html(self, mock_css):
        """Test generating PDF from multiple HTML contents."""
        # Create mock HTML objects and rendered documents
        mock_html_instances = []
        mock_rendered_docs = []
        
        # Setup base doc with mock pages
        mock_base_doc = MagicMock()
        
        # Setup mocks for HTML class
        with patch('cvgenai.services.pdf_service.HTML') as mock_html_class:
            # Configure mocks for each HTML instance
            for i in range(2):
                mock_instance = MagicMock()
                mock_doc = MagicMock()
                mock_html_instances.append(mock_instance)
                mock_rendered_docs.append(mock_doc)
            
            # First mock will return the base doc when rendered
            mock_html_instances[0].render.return_value = mock_base_doc
            # Second mock will return a doc whose pages we want to append
            mock_html_instances[1].render.return_value = mock_rendered_docs[1]
            
            # Set side_effect to return different mock HTML instances
            mock_html_class.side_effect = mock_html_instances
            
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = Path(temp_dir) / "test_multiple.pdf"
                
                # Test data
                html_contents = [
                    "<html><body><h1>Page 1</h1></body></html>",
                    "<html><body><h1>Page 2</h1></body></html>"
                ]
                css_path = 'test/style.css'
                
                # Create service and generate PDF
                service = PDFService(css_path=css_path)
                service.generate_pdf_from_multiple_html(html_contents, str(output_path))
                
                # Verify HTML instances were created with correct content
                assert mock_html_class.call_count == 2
                mock_html_class.assert_any_call(string=html_contents[0])
                mock_html_class.assert_any_call(string=html_contents[1])
                
                # Verify render was called for all HTML instances with correct CSS
                for i, instance in enumerate(mock_html_instances):
                    instance.render.assert_called_once()
                    # Check that CSS was passed to render
                    css_arg = instance.render.call_args[1]['stylesheets'][0]
                    assert css_arg is mock_css.return_value
                
                # Verify the pages were extended
                mock_base_doc.pages.extend.assert_called_once_with(mock_rendered_docs[1].pages)
                
                # Verify PDF was written
                mock_base_doc.write_pdf.assert_called_once_with(str(output_path))