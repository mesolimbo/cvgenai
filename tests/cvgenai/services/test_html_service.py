"""Tests for the html_service module."""

import tempfile
from pathlib import Path
from cvgenai.services.html_service import HTMLService


class TestHTMLService:
    """Test cases for the HTMLService class."""

    def test_save_html(self):
        """Test saving HTML content to a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Define test content and path
            html_content = "<html><body><h1>Test Title</h1></body></html>"
            output_path = Path(temp_dir) / "test_output.html"
            
            # Save the HTML content
            HTMLService.save_html(html_content, output_path)
            
            # Verify the file was created
            assert output_path.exists()
            assert output_path.is_file()
            
            # Check that the content was saved correctly
            with open(output_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
                assert saved_content == html_content
    
    def test_save_html_with_string_path(self):
        """Test saving HTML content using a string path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Define test content and path
            html_content = "<html><body><h1>String Path Test</h1></body></html>"
            output_path_str = str(Path(temp_dir) / "string_path_test.html")
            
            # Save the HTML content
            HTMLService.save_html(html_content, output_path_str)
            
            # Verify the file was created
            path_obj = Path(output_path_str)
            assert path_obj.exists()
            assert path_obj.is_file()
            
            # Check that the content was saved correctly
            with open(path_obj, 'r', encoding='utf-8') as f:
                saved_content = f.read()
                assert saved_content == html_content
    
    def test_save_html_creates_parent_directories(self):
        """Test that saving HTML creates parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Define a nested path that doesn't exist yet
            nested_dir = Path(temp_dir) / "parent" / "child"
            output_path = nested_dir / "nested_test.html"
            html_content = "<html><body><h1>Nested Test</h1></body></html>"
            
            # Save HTML to the nested path (should create directories)
            output_path.parent.mkdir(parents=True, exist_ok=True)  # Create parent directories
            HTMLService.save_html(html_content, output_path)
            
            # Verify the file was created
            assert output_path.exists()
            assert output_path.is_file()
            
            # Check the content
            with open(output_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
                assert saved_content == html_content