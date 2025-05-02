"""Tests for the cli module."""

import pytest
from unittest.mock import patch, MagicMock, call
from argparse import Namespace

import cvgenai.cli as cli


class TestCLI:
    """Test cases for command-line interface functions."""

    @patch('cvgenai.cli.Factory')
    def test_main_initialization(self, mock_factory_class):
        """Test the initialization of the Factory in main function."""
        # Setup mock
        mock_factory_instance = MagicMock()
        mock_factory_class.return_value = mock_factory_instance
        mock_args = Namespace(content='test_resume.toml')
        mock_factory_instance.parse_args.return_value = mock_args
        mock_factory_instance.get_generators_to_run.return_value = []
        mock_factory_instance.get_enabled_generators.return_value = []
        
        # Set up app_config with a string value for content_path_arg
        mock_factory_instance.app_config = {'cli': {'content_path_arg': 'content'}}
        
        # Call function
        cli.main()
        
        # Verify Factory was initialized with correct config path
        mock_factory_class.assert_called_once_with('app_config.toml')
        # Verify args were parsed
        mock_factory_instance.parse_args.assert_called_once()
    
    @patch('cvgenai.cli.Factory')
    @patch('cvgenai.cli.os.environ.get')
    def test_main_with_custom_config_path(self, mock_environ_get, mock_factory_class):
        """Test main function with a custom config path from environment variable."""
        # Setup mocks
        mock_environ_get.return_value = 'custom_config.toml'
        mock_factory_instance = MagicMock()
        mock_factory_class.return_value = mock_factory_instance
        mock_args = Namespace(content='test_resume.toml')
        mock_factory_instance.parse_args.return_value = mock_args
        mock_factory_instance.get_generators_to_run.return_value = []
        mock_factory_instance.get_enabled_generators.return_value = []
        
        # Set up app_config with a string value for content_path_arg
        mock_factory_instance.app_config = {'cli': {'content_path_arg': 'content'}}
        
        # Call function
        cli.main()
        
        # Verify Factory was initialized with custom config path
        mock_environ_get.assert_called_once_with('APP_CONFIG_PATH', 'app_config.toml')
        mock_factory_class.assert_called_once_with('custom_config.toml')
    
    @patch('cvgenai.cli.Factory')
    def test_main_generator_execution(self, mock_factory_class):
        """Test that generators are correctly executed in main."""
        # Setup mocks
        mock_factory_instance = MagicMock()
        mock_factory_class.return_value = mock_factory_instance
        
        # Mock args
        mock_args = Namespace(content='test_resume.toml')
        mock_factory_instance.parse_args.return_value = mock_args
        
        # Mock generators to run
        mock_factory_instance.get_generators_to_run.return_value = ['resume', 'cover_letter']
        
        # Mock enabled generators
        mock_factory_instance.get_enabled_generators.return_value = [
            {'name': 'resume', 'description': 'Resume Generator'},
            {'name': 'cover_letter', 'description': 'Cover Letter Generator'}
        ]
        
        # Mock app config
        mock_factory_instance.app_config = {'cli': {'content_path_arg': 'content'}}
        
        # Mock generator instances
        mock_resume_generator = MagicMock()
        mock_cover_letter_generator = MagicMock()
        
        # Configure create_generator to return different generators based on name
        mock_factory_instance.create_generator.side_effect = lambda name: {
            'resume': mock_resume_generator,
            'cover_letter': mock_cover_letter_generator
        }[name]
        
        # Call function
        cli.main()
        
        # Verify that both generators were created and called
        assert mock_factory_instance.create_generator.call_count == 2
        mock_factory_instance.create_generator.assert_has_calls([
            call('resume'),
            call('cover_letter')
        ])
        
        # Verify both generators were executed with correct arguments
        mock_resume_generator.generate.assert_called_once_with(args=mock_args)
        mock_cover_letter_generator.generate.assert_called_once_with(args=mock_args)
    
    @patch('cvgenai.cli.Factory')
    @patch('builtins.print')
    def test_main_with_generator_error(self, mock_print, mock_factory_class):
        """Test error handling when a generator raises an exception."""
        # Setup mocks
        mock_factory_instance = MagicMock()
        mock_factory_class.return_value = mock_factory_instance
        
        # Mock args
        mock_args = Namespace(content='test_resume.toml')
        mock_factory_instance.parse_args.return_value = mock_args
        
        # Mock generators to run
        mock_factory_instance.get_generators_to_run.return_value = ['resume', 'cover_letter']
        
        # Mock enabled generators
        mock_factory_instance.get_enabled_generators.return_value = [
            {'name': 'resume', 'description': 'Resume Generator'},
            {'name': 'cover_letter', 'description': 'Cover Letter Generator'}
        ]
        
        # Mock app config
        mock_factory_instance.app_config = {'cli': {'content_path_arg': 'content'}}
        
        # Mock generator instances
        mock_resume_generator = MagicMock()
        mock_cover_letter_generator = MagicMock()
        
        # Make the resume generator raise an exception
        mock_resume_generator.generate.side_effect = Exception("Test error")
        
        # Configure create_generator to return different generators based on name
        mock_factory_instance.create_generator.side_effect = lambda name: {
            'resume': mock_resume_generator,
            'cover_letter': mock_cover_letter_generator
        }[name]
        
        # Call function
        cli.main()
        
        # Verify error handling: should print error message but continue execution
        mock_print.assert_any_call("Error generating resume: Test error")
        
        # Verify the second generator was still executed despite the first one failing
        mock_cover_letter_generator.generate.assert_called_once_with(args=mock_args)
        
    @patch('cvgenai.cli.Factory')
    @patch('builtins.print')
    def test_main_prints_correct_information(self, mock_print, mock_factory_class):
        """Test that main prints the expected information."""
        # Setup mocks
        mock_factory_instance = MagicMock()
        mock_factory_class.return_value = mock_factory_instance
        
        # Mock args
        mock_args = Namespace(content='test_resume.toml')
        mock_factory_instance.parse_args.return_value = mock_args
        
        # Mock generators to run
        mock_factory_instance.get_generators_to_run.return_value = ['resume']
        
        # Mock enabled generators
        mock_factory_instance.get_enabled_generators.return_value = [
            {'name': 'resume', 'description': 'Resume Generator'}
        ]
        
        # Mock app config and other required methods
        mock_factory_instance.app_config = {'cli': {'content_path_arg': 'content'}}
        mock_factory_instance.create_generator.return_value = MagicMock()
        
        # Call function
        cli.main()
        
        # Verify print statements
        mock_print.assert_any_call("Generating documents with the following options:")
        mock_print.assert_any_call("- Resume Generator")
        mock_print.assert_any_call("Using content from: test_resume.toml")
        mock_print.assert_any_call("---")
        mock_print.assert_any_call("\nGeneration completed successfully!")