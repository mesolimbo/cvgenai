"""HTML generation service for CV Generation."""

from pathlib import Path


class HTMLService:
    """Service for handling HTML content."""

    @staticmethod
    def save_html(html_content, output_path):
        """Save HTML string to a file.
        
        Args:
            html_content (str): The HTML content to save
            output_path (str or Path): Path where to save the HTML file
        """
        # Convert to string if it's a Path object
        if isinstance(output_path, Path):
            output_path = str(output_path)
            
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
