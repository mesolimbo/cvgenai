"""File operations service for CV Generation."""

import shutil
from pathlib import Path


class FileService:
    """Service for handling file operations."""
    
    def ensure_directory(self, directory_path):
        """Create directory if it doesn't exist and return path."""
        path = Path(directory_path)
        path.mkdir(exist_ok=True)
        return path
    
    def copy_css(self, css_source_path, output_dir):
        """Copy the CSS file to the output directory."""
        css_source = Path(css_source_path)
        css_dest = output_dir / css_source.name
        shutil.copy2(css_source, css_dest)
        return css_dest
