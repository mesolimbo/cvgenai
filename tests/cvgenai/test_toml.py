"""Tests for the TOML configuration manager."""
import os
from pathlib import Path
import pytest
import shutil
import tempfile

from cvgenai.config import ConfigManager


class TestConfigManager:
    """Test cases for the ConfigManager class."""

    @staticmethod
    def test_load_valid_toml():
        """Test loading a valid TOML file."""
        current_dir = os.getcwd()
        temp_dir = os.path.join(current_dir, "temp_test_dir")

        try:
            os.makedirs(temp_dir, exist_ok=True)
            temp_file_path = os.path.join(temp_dir, "config.toml")
            with open(temp_file_path, "wb") as tmp:
                tmp.write(b'''
                    [app]
                    name = "CVGenAI"
                    version = "1.0.0"

                    [settings]
                    template_dir = "templates"
                    output_dir = "output"
                ''')

            # Test with ConfigManager
            config_manager = ConfigManager()
            config = config_manager.load(temp_file_path)

            assert config["app"]["name"] == "CVGenAI"
            assert config["app"]["version"] == "1.0.0"
            assert config["settings"]["template_dir"] == "templates"
            assert config["settings"]["output_dir"] == "output"

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

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

    @staticmethod
    def test_load_with_customizer(tmp_path):
        """Test load supports a customizer returning modified TOML."""
        content = "[section]\nname = 'orig'"
        project_root = Path(__file__).resolve().parents[2]
        test_dir = project_root / "temp_customizer"
        test_dir.mkdir(exist_ok=True)
        file_path = test_dir / "resume.toml"
        file_path.write_text(content)

        def customizer(_: str) -> str:
            return "[section]\nname = 'custom'"

        manager = ConfigManager()
        result = manager.load(str(file_path), customizer)
        assert result == {"section": {"name": "custom"}}
        shutil.rmtree(test_dir)
