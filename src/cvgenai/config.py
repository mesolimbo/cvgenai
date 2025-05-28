"""TOML configuration manager for CV Gen AI."""

import tomli
from abc import ABC, abstractmethod

# Config loader interface
class IConfigLoader(ABC):
    """Interface for configuration loaders."""
    
    @abstractmethod
    def load(self, config_path):
        """Load configuration from a file path."""
        pass

# Reference TOML ConfigLoader Implementation
class ConfigManager(IConfigLoader):
    """TOML configuration manager."""
    
    def load(self, config_path):
        """Load configuration from TOML file.
        
        Args:
            config_path: Path to the TOML configuration file

        Returns:
            dict: Loaded configuration
        """
        if not config_path.endswith('.toml'):
            raise ValueError("Invalid configuration file format. Expected a .toml file.")

        with open(config_path, 'rb') as f:
            return tomli.load(f)
