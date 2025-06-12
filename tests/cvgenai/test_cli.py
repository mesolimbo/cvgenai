"""Tests for the cli module."""

from unittest.mock import patch, MagicMock, call
from argparse import Namespace

from cvgenai.cli import CLI


class TestCLI:
    """Test cases for command-line interface functions."""

    @patch('cvgenai.cli.CLI.initialize_factory')
    @patch('cvgenai.cli.load_dotenv')
    def test_main_initialization(self, mock_load_dotenv, mock_initialize_factory):
        """Test the initialization of the Factory in main function."""
        # Setup mock
        mock_factory_instance = MagicMock()
        mock_initialize_factory.return_value = mock_factory_instance
        mock_factory_instance.args = {'content': 'test_resume.toml'}
        mock_factory_instance.get_generators_to_run.return_value = []
        mock_factory_instance.get_enabled_generators.return_value = []

        # Set up app_config with a string value for content_path_arg
        mock_factory_instance.app_config = {'cli': {'content_path_arg': 'content'}}

        # Patch the initialize_career method
        with patch('cvgenai.cli.CLI.initialize_career') as mock_initialize_career:
            mock_career_instance = MagicMock()
            mock_initialize_career.return_value = mock_career_instance
            
            # Call function
            CLI.main()

            # Verify Factory was initialized with correct config path
            mock_initialize_factory.assert_called_once()
            mock_initialize_career.assert_called_once_with(mock_factory_instance)


    @patch('cvgenai.cli.Career')
    def test_initialize_career(self, mock_career_class):
        """Test the initialization of Career in CLI."""
        # Setup mocks
        mock_factory = MagicMock()
        mock_factory.app_config = {'cli': {'content_path_arg': 'content'}}
        mock_factory.args = {'content': 'test_resume.toml'}
        
        mock_config_manager = MagicMock()
        mock_factory.get_service.return_value = mock_config_manager
        
        mock_career_instance = MagicMock()
        mock_career_class.return_value = mock_career_instance
        
        # Call method
        result = CLI.initialize_career(mock_factory)
        
        # Verify Career was created with config_manager
        mock_factory.get_service.assert_called_once_with('config_manager')
        mock_career_class.assert_called_once_with(mock_config_manager)
        
        # Verify career.load was called with correct path
        mock_career_instance.load.assert_called_once_with('test_resume.toml')
        
        # Verify correct instance was returned
        assert result == mock_career_instance


    @patch('cvgenai.factory.Factory.get_service', return_value=MagicMock())
    @patch('cvgenai.factory.Factory._parse_args')
    @patch('cvgenai.config.ConfigManager.load', return_value={})
    @patch('cvgenai.cli.os.environ.get')
    def test_main_with_custom_config_path(self, mock_environ_get, mock_load_app_config, _, __):
        """Test main function with a custom config path from environment variable."""
        # Setup mock for environment variable
        mock_environ_get.return_value = 'custom_config.toml'

        # Call the initialize_factory method directly
        CLI.initialize_factory()

        # Verify environment variable was checked
        mock_environ_get.assert_called_once_with('APP_CONFIG_PATH', 'app_config.toml')

        # Verify the factory attempted to load the custom config
        mock_load_app_config.assert_called_once_with('custom_config.toml')


    @staticmethod
    def set_up_mocks(mock_initialize_factory, mock_initialize_career=None):
        # Setup mocks
        mock_factory_instance = MagicMock()
        mock_initialize_factory.return_value = mock_factory_instance
        # Mock args
        mock_factory_instance.args = {'content': 'test_resume.toml'}
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
        
        # Mock career instance if provided
        if mock_initialize_career:
            mock_career_instance = MagicMock()
            mock_initialize_career.return_value = mock_career_instance
            return mock_cover_letter_generator, mock_factory_instance, mock_resume_generator, mock_career_instance
        else:
            return mock_cover_letter_generator, mock_factory_instance, mock_resume_generator


    @patch('cvgenai.cli.CLI.initialize_factory')
    @patch('cvgenai.cli.CLI.initialize_career')
    def test_main_generator_execution(self, mock_initialize_career, mock_initialize_factory):
        """Test that generators are correctly executed in main."""
        (mock_cover_letter_generator,
         mock_factory_instance,
         mock_resume_generator,
         mock_career_instance) = self.set_up_mocks(mock_initialize_factory, mock_initialize_career)

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
        mock_resume_generator.generate.assert_called_once_with(args=mock_factory_instance.args, career=mock_career_instance)
        mock_cover_letter_generator.generate.assert_called_once_with(args=mock_factory_instance.args, career=mock_career_instance)


    @patch('cvgenai.cli.CLI.initialize_factory')
    @patch('cvgenai.cli.CLI.initialize_career')
    @patch('builtins.print')
    def test_main_with_generator_error(self, mock_print, mock_initialize_career, mock_initialize_factory):
        """Test error handling when a generator raises an exception."""
        (mock_cover_letter_generator,
         mock_factory_instance,
         mock_resume_generator,
         mock_career_instance) = self.set_up_mocks(mock_initialize_factory, mock_initialize_career)

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
        mock_cover_letter_generator.generate.assert_called_once_with(args=mock_factory_instance.args, career=mock_career_instance)
