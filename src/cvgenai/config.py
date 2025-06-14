"""TOML configuration manager for CV Gen AI."""

from abc import ABC, abstractmethod
import os

import tomli

# Config loader interface
class IConfigLoader(ABC):
    """Interface for configuration loaders."""
    
    @abstractmethod
    def load(self, config_path, customize_lambda=None):
        """Load configuration from a file path."""
        pass

# Reference TOML ConfigLoader Implementation
class ConfigManager(IConfigLoader):
    """TOML configuration manager."""
    
    def load(self, config_path, customize_lambda=None):
        """Load configuration from TOML file.
        
        Args:
            config_path: Path to the TOML configuration file or a TOML string
            customize_lambda: Optional lambda function to modify the content before loading

        Returns:
            dict: Loaded configuration
        """
        # Raise an error if the file is outside the current directory
        current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        config_full_path = os.path.abspath(config_path)

        if not config_full_path.startswith(current_dir):
            raise ValueError(f"Configuration file path must be within the project directory: {current_dir}")

        with open(config_full_path, 'rb') as f:
            # Read content of file as string
            content = f.read().decode('utf-8')

            # Use customizer lambda service to modify the content
            if customize_lambda:
                content = customize_lambda(content)

            return tomli.loads(content)
