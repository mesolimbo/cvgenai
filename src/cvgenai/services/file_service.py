"""File operations service for CV Generation."""

import shutil
from pathlib import Path
from typing import Optional


class FileService:
    """Service for handling file operations."""

    @staticmethod
    def ensure_directory(directory_path):
        """Create directory if it doesn't exist and return path."""
        path = Path(directory_path)
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def copy_css(css_source_path, output_dir, generate_html=False):
        """
        Copy the CSS file to the output directory.

        Args:
            css_source_path: Path to the CSS source file
            output_dir: Directory where to copy the CSS file
            generate_html: Only copy if this is True (HTML generation is enabled)

        Returns:
            Path: Path to the copied CSS file or None if not copied
        """
        if not generate_html:
            return None

        css_source = Path(css_source_path)
        css_dest = output_dir / css_source.name
        shutil.copy2(css_source, css_dest)
        return css_dest
