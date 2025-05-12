"""Tests for the TOML configuration manager."""

import os
import pytest
import tempfile
from cvgenai.config.toml import ConfigManager, load_config


class TestConfigManager:
    """Test cases for the ConfigManager class."""

    @staticmethod
    def test_load_valid_toml():
        """Test loading a valid TOML file."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".toml") as tmp:
            tmp.write(b'''
                [app]
                name = "CVGenAI"
                version = "1.0.0"
                
                [settings]
                template_dir = "templates"
                output_dir = "output"
            ''')
            tmp_path = tmp.name

        try:
            # Test with ConfigManager
            config_manager = ConfigManager()
            config = config_manager.load(tmp_path)
            
            assert config["app"]["name"] == "CVGenAI"
            assert config["app"]["version"] == "1.0.0"
            assert config["settings"]["template_dir"] == "templates"
            assert config["settings"]["output_dir"] == "output"
            
            # Test with legacy function
            legacy_config = load_config(tmp_path)
            assert legacy_config == config
        finally:
            os.unlink(tmp_path)

    @staticmethod
    def test_load_nonexistent_file():
        """Test loading a non-existent file raises FileNotFoundError."""
        config_manager = ConfigManager()
        with pytest.raises(FileNotFoundError):
            config_manager.load("nonexistent_file.toml")

    @staticmethod
    def test_load_invalid_toml():
        """Test loading an invalid TOML file raises an error."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as tmp:
            tmp.write(b'''
                [app
                name = "CVGenAI"
            ''')  # Invalid TOML syntax
            tmp_path = tmp.name

        try:
            config_manager = ConfigManager()
            with pytest.raises(Exception):  # tomli would raise a TOMLDecodeError
                config_manager.load(tmp_path)
        finally:
            os.unlink(tmp_path)