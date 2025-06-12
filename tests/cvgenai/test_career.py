"""Tests for the Career class."""

import pytest
from unittest.mock import MagicMock

from cvgenai.career import Career
from cvgenai.config import IConfigLoader


class TestCareer:
    """Tests for the Career class."""

    @staticmethod
    def test_load():
        """Test loading career data."""
        # Arrange
        mock_config_manager = MagicMock(spec=IConfigLoader)
        mock_config_manager.load.return_value = {"personal": {"name": "Test User"}}
        content_path = "test_resume.toml"
        
        # Act
        career = Career(mock_config_manager)
        career_data = career.load(content_path)
        
        # Assert
        mock_config_manager.load.assert_called_once_with(content_path)
        assert career_data == {"personal": {"name": "Test User"}}

    @staticmethod
    def test_factory_init():
        """Test initializing with factory."""
        # Arrange
        mock_factory = MagicMock()
        mock_config_manager = MagicMock(spec=IConfigLoader)
        mock_factory.get_service.return_value = mock_config_manager
        
        # This test is no longer applicable as the Career class now takes a config_manager directly
        # instead of a factory. We'll test that config_manager is passed directly.
        
        # Act
        career = Career(config_manager=mock_config_manager)
        
        # Assert
        assert career._config_manager == mock_config_manager

    @staticmethod
    def test_get_data():
        """Test getting loaded career data."""
        # Arrange
        mock_config_manager = MagicMock(spec=IConfigLoader)
        mock_config_manager.load.return_value = {"personal": {"name": "Test User"}}
        career = Career(mock_config_manager)
        career.load("test_resume.toml")
        
        # Act
        career_data = career.get_data()
        
        # Assert
        assert career_data == {"personal": {"name": "Test User"}}

    @staticmethod
    def test_get_data_not_loaded():
        """Test getting career data when not loaded."""
        # Arrange
        mock_config_manager = MagicMock(spec=IConfigLoader)
        career = Career(mock_config_manager)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Career data not loaded"):
            career.get_data()

    @staticmethod
    def test_load_no_config_manager():
        """Test loading career without a config manager."""
        # This test is no longer applicable since config_manager is now required in the constructor
        # We'll test what happens when we try to load with an invalid path instead
        
        # Arrange
        mock_config_manager = MagicMock(spec=IConfigLoader)
        mock_config_manager.load.side_effect = FileNotFoundError("File not found")
        career = Career(mock_config_manager)
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            career.load("invalid_path.toml")
