"""File operations service for CV Generation."""

import shutil
from pathlib import Path


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

    @staticmethod
    def safe_read(file_path: str) -> str:
        """Safely read a file ensuring it resides in the project directory.

        Parameters
        ----------
        file_path:
            Path to the file to read.

        Returns
        -------
        str
            Contents of the file as text.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If the file path is outside the project directory.
        """
        project_root = Path(__file__).resolve().parents[3]
        abs_path = Path(file_path).resolve()

        if not str(abs_path).startswith(str(project_root)):
            raise ValueError(
                f"File {abs_path} must be within the project directory: {project_root}"
            )

        with abs_path.open('r', encoding='utf-8') as f:
            return f.read()
