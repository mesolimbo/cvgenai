"""Tests for the cli module."""

from unittest.mock import patch, MagicMock, call
from argparse import Namespace

from cvgenai.cli import CLI


class TestCLI:
    """Test cases for command-line interface functions."""

    @patch('cvgenai.cli.CLI.initialize_factory')
    def test_main_initialization(self, mock_initialize_factory):
        """Test the initialization of the Factory in main function."""
        # Setup mock
        mock_factory_instance = MagicMock()
        mock_initialize_factory.return_value = mock_factory_instance
        mock_args = Namespace(content='test_resume.toml')
        mock_factory_instance.parse_args.return_value = mock_args
        mock_factory_instance.get_generators_to_run.return_value = []
        mock_factory_instance.get_enabled_generators.return_value = []

        # Set up app_config with a string value for content_path_arg
        mock_factory_instance.app_config = {'cli': {'content_path_arg': 'content'}}

        # Call function
        CLI.main()

        # Verify Factory was initialized with correct config path
        mock_initialize_factory.assert_called_once()
        # Verify args were parsed
        mock_factory_instance.parse_args.assert_called_once()

    @patch('cvgenai.cli.os.environ.get')
    def test_main_with_custom_config_path(self, mock_environ_get):
        """Test main function with a custom config path from environment variable."""
        # Setup mock
        mock_environ_get.return_value = 'custom_config.toml'

        # We need to patch sys.argv to avoid command line parsing issues
        with patch('sys.argv', ['cvgenai']):
            # Call the initialize_factory method directly instead of main
            # This allows us to test just the part we care about
            CLI.initialize_factory()

        # Verify environment variable was checked with correct parameters
        mock_environ_get.assert_called_once_with('APP_CONFIG_PATH', 'app_config.toml')

    @patch('cvgenai.cli.CLI.initialize_factory')
    def test_main_generator_execution(self, mock_initialize_factory):
        """Test that generators are correctly executed in main."""
        # Setup mocks
        mock_factory_instance = MagicMock()
        mock_initialize_factory.return_value = mock_factory_instance

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
        CLI.main()

        # Verify that both generators were created and called
        assert mock_factory_instance.create_generator.call_count == 2
        mock_factory_instance.create_generator.assert_has_calls([
            call('resume'),
            call('cover_letter')
        ])

        # Verify both generators were executed with correct arguments
        mock_resume_generator.generate.assert_called_once_with(args=mock_args)
        mock_cover_letter_generator.generate.assert_called_once_with(args=mock_args)

    @patch('cvgenai.cli.CLI.initialize_factory')
    @patch('builtins.print')
    def test_main_with_generator_error(self, mock_print, mock_initialize_factory):
        """Test error handling when a generator raises an exception."""
        # Setup mocks
        mock_factory_instance = MagicMock()
        mock_initialize_factory.return_value = mock_factory_instance

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
        CLI.main()

        # Verify error handling: should print error message but continue execution
        mock_print.assert_any_call("Error generating resume: Test error")

        # Verify the second generator was still executed despite the first one failing
        mock_cover_letter_generator.generate.assert_called_once_with(args=mock_args)
