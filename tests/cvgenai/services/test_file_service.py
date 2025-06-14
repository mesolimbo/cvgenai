"""Tests for the file_service module."""

import tempfile
from pathlib import Path
import pytest
from cvgenai.services.file_service import FileService


class TestFileService:
    """Test cases for the FileService class."""

    @staticmethod
    def test_ensure_directory():
        """Test creating a directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as base_dir:
            # Create a path for a directory that doesn't exist yet
            test_dir = Path(base_dir) / "test_directory"
            
            # Use FileService to create the directory
            created_path = FileService.ensure_directory(str(test_dir))
            
            # Check that the directory was created
            assert test_dir.exists()
            assert test_dir.is_dir()
            assert created_path == test_dir
            
            # Test that calling it again on an existing directory doesn't raise errors
            created_path_2 = FileService.ensure_directory(str(test_dir))
            assert created_path_2 == test_dir

    @staticmethod
    def test_copy_css():
        """Test copying a CSS file to an output directory when generate_html is True."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create source directory and CSS file
            source_dir = Path(temp_dir) / "source"
            source_dir.mkdir()
            css_file = source_dir / "style.css"
            css_content = "body { font-family: Arial; }"
            
            with open(css_file, 'w') as f:
                f.write(css_content)
            
            # Create output directory
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir()
            
            # Copy the CSS file with generate_html=True
            dest_path = FileService.copy_css(css_file, output_dir, generate_html=True)
            
            # Check that the file was copied correctly
            assert dest_path is not None
            assert dest_path.exists()
            assert dest_path.is_file()
            assert dest_path == output_dir / "style.css"
            
            # Verify the content is the same
            with open(dest_path, 'r') as f:
                copied_content = f.read()
                assert copied_content == css_content
                
    @staticmethod
    def test_copy_css_without_html_flag():
        """Test that CSS is not copied when generate_html is False."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create source directory and CSS file
            source_dir = Path(temp_dir) / "source"
            source_dir.mkdir()
            css_file = source_dir / "style.css"
            css_content = "body { font-family: Arial; }"
            
            with open(css_file, 'w') as f:
                f.write(css_content)
            
            # Create output directory
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir()
            
            # Call copy_css with generate_html=False
            result = FileService.copy_css(css_file, output_dir, generate_html=False)
            
            # Check that no file was copied and None was returned
            assert result is None
            assert not (output_dir / "style.css").exists()

    @staticmethod
    def test_safe_read():
        """Test reading a file safely within the project root."""
        project_root = Path(__file__).resolve().parents[3] / "src"
        test_file = project_root / "sample_safe_read.txt"
        test_file.write_text("hello")

        try:
            result = FileService.safe_read(str(test_file))
            assert result == "hello"
        finally:
            test_file.unlink()

    @staticmethod
    def test_safe_read_outside_root(tmp_path):
        """Test safe_read raises ValueError for paths outside the project root."""
        # Create file outside project root using tmp_path
        file_path = tmp_path / 'outside.txt'
        file_path.write_text('oops')

        try:
            with pytest.raises(ValueError):
                FileService.safe_read(str(file_path))
        finally:
            file_path.unlink()

