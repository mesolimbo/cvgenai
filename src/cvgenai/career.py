"""Career data management for CV Generation."""
from typing import Dict, Any

from cvgenai.config import IConfigLoader

class Career:
    """Class for managing career data and configuration."""
    def __init__(self, config_manager: IConfigLoader):
        """Initialize the career manager.
        
        Args:
            config_manager: Config manager instance for loading content
        """
        self._config_manager = config_manager
        self._career_data = None
    
    def load(self, content_path: str, customize_lambda=None) -> Dict[str, Any]:
        """Load career data from the content file.
        
        Args:
            content_path: Path to the content file (usually a TOML file)
            customize_lambda: Optional lambda function to modify the content before loading
            
        Returns:
            dict: Loaded career data configuration
        """
        self._career_data = self._config_manager.load(content_path, customize_lambda)
        return self._career_data
    
    def get_data(self) -> Dict[str, Any]:
        """Get the currently loaded career data.
        
        Returns:
            dict: Current career data or None if not loaded
        """
        if self._career_data is None:
            raise ValueError("Career data not loaded. Please call load first.")
            
        return self._career_data
