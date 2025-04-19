"""TOML configuration loader for CV Gen AI."""

import tomli
from pathlib import Path


def load_config(config_path):
    """Load configuration from TOML file.
    
    Args:
        config_path: Path to the TOML configuration file
        
    Returns:
        dict: Loaded configuration
    """
    with open(config_path, 'rb') as f:
        return tomli.load(f)
