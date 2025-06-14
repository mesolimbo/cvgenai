"""TOML configuration manager for CV Gen AI."""
from abc import ABC, abstractmethod
from pathlib import Path

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
    def load(self, config_source, customize_lambda=None):
        """Load configuration from TOML text or file.

        Args:
            config_source: Path to the TOML configuration file or a TOML string
            customize_lambda: Optional lambda function to modify the content before loading

        Returns:
            dict: Loaded configuration
        """
        source_path = Path(str(config_source))
        if source_path.is_file():
            content = source_path.read_text(encoding='utf-8')
        elif source_path.suffix == '.toml':
            raise FileNotFoundError(str(config_source))
        else:
            content = str(config_source)

        if customize_lambda:
            content = customize_lambda(content)

        return tomli.loads(content)
