"""Tests for the controller module."""
from unittest.mock import patch, MagicMock, call

from cvgenai.controller import CVGenController


class TestCVGenController:
    """Test cases for the CVGenController class."""

    @patch('cvgenai.controller.Factory')
    @patch('cvgenai.controller.Career')
    def test_initialize(self, mock_career_class, mock_factory_class):
        """Test controller initialization."""
        # Setup mocks
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.app_config = {'cli': {'content_path_arg': 'content'}}
        mock_factory.args = {'content': 'test_resume.toml'}
        
        mock_config_manager = MagicMock()
        mock_file_service = MagicMock()
        mock_file_service.safe_read.return_value = 'resume_data'
        mock_customizer = MagicMock()
        mock_factory.get_service.side_effect = [
            mock_config_manager,
            mock_file_service,
            mock_customizer,
        ]
        
        mock_career = MagicMock()
        mock_career_class.return_value = mock_career
        
        # Create and initialize controller
        controller = CVGenController()
        
        # Verify initialization steps
        mock_factory_class.assert_called_once()
        mock_career_class.assert_called_once_with(mock_config_manager)
        mock_file_service.safe_read.assert_any_call('test_resume.toml')
        mock_career.load.assert_called_once_with('resume_data', None)
        
        assert controller.factory == mock_factory
        assert controller.career == mock_career

    @patch.dict('os.environ', {'APP_CONFIG_PATH': 'custom_config.toml'})
    @patch('cvgenai.controller.Factory')
    def test_initialize_factory_with_custom_config(self, mock_factory_class):
        """Test factory initialization with custom config path."""
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory
        
        controller = CVGenController()
        result = controller._initialize_factory()
        
        # Verify factory was created with custom config path
        mock_factory_class.assert_called_with('custom_config.toml')
        assert result == mock_factory

    @patch('cvgenai.controller.Factory')
    @patch('cvgenai.controller.Career')
    def test_initialize_career(self, mock_career_class, *_):
        """Test career initialization."""
        # Setup controller with mock factory
        controller = CVGenController()
        controller.factory = MagicMock()
        controller.factory.app_config = {'cli': {'content_path_arg': 'content'}}
        controller.factory.args = {'content': 'test_resume.toml'}

        mock_config_manager = MagicMock()
        mock_file_service = MagicMock()
        mock_file_service.safe_read.return_value = 'resume_data'
        mock_customizer = MagicMock()
        controller.factory.get_service.side_effect = [
            mock_config_manager,
            mock_file_service,
            mock_customizer,
        ]
        
        mock_career = MagicMock()
        mock_career_class.return_value = mock_career
        
        # Call method
        result = controller._initialize_career()
        
        # Verify career initialization
        controller.factory.get_service.assert_has_calls([
            call('config_manager'),
            call('file_service'),
            call('customizer_service'),
        ])
        mock_file_service.safe_read.assert_any_call('test_resume.toml')
        mock_career_class.assert_called_with(mock_config_manager)
        mock_career.load.assert_called_with('resume_data', None)
        assert result == mock_career

    @staticmethod
    @patch('cvgenai.controller.Factory')
    @patch('cvgenai.controller.Career')
    def test_get_generation_info(*_):
        """Test getting generation information."""
        # Setup controller with mock factory
        controller = CVGenController()
        controller.factory = MagicMock()
        
        # Setup mock data
        generators_to_run = ['resume', 'cover_letter']
        enabled_generators = [
            {'name': 'resume', 'description': 'Resume Generator'},
            {'name': 'cover_letter', 'description': 'Cover Letter Generator'}
        ]
        
        controller.factory.get_generators_to_run.return_value = generators_to_run
        controller.factory.get_enabled_generators.return_value = enabled_generators
        controller.factory.app_config = {'cli': {'content_path_arg': 'content'}}
        controller.factory.args = {'content': 'test_resume.toml'}
        
        # Call method
        result_generators, result_enabled, result_path = controller.get_generation_info()
        
        # Verify results
        assert result_generators == generators_to_run
        assert result_enabled == enabled_generators
        assert result_path == 'test_resume.toml'

    @staticmethod
    @patch('cvgenai.controller.Factory')
    @patch('cvgenai.controller.Career')
    def test_generate_documents_success(*_):
        """Test successful document generation."""
        # Setup controller
        controller = CVGenController()
        controller.factory = MagicMock()
        controller.career = MagicMock()
        
        # Setup mock generators
        mock_resume_generator = MagicMock()
        mock_cover_letter_generator = MagicMock()
        
        controller.factory.get_generators_to_run.return_value = ['resume', 'cover_letter']
        controller.factory.get_enabled_generators.return_value = []
        controller.factory.app_config = {'cli': {'content_path_arg': 'content'}}
        controller.factory.args = {'content': 'test_resume.toml'}
        
        # Configure create_generator to return different generators
        controller.factory.create_generator.side_effect = lambda name: {
            'resume': mock_resume_generator,
            'cover_letter': mock_cover_letter_generator
        }[name]
        
        # Call method
        errors = controller.generate_documents()
        
        # Verify no errors
        assert errors == []
        
        # Verify generators were called
        mock_resume_generator.generate.assert_called_once_with(
            args=controller.factory.args, career=controller.career
        )
        mock_cover_letter_generator.generate.assert_called_once_with(
            args=controller.factory.args, career=controller.career
        )

    @staticmethod
    @patch('cvgenai.controller.Factory')
    @patch('cvgenai.controller.Career')
    def test_generate_documents_with_errors(*_):
        """Test document generation with errors."""
        # Setup controller
        controller = CVGenController()
        controller.factory = MagicMock()
        controller.career = MagicMock()
        
        # Setup mock generators
        mock_resume_generator = MagicMock()
        mock_resume_generator.generate.side_effect = Exception("Resume generation failed")
        
        mock_cover_letter_generator = MagicMock()
        
        controller.factory.get_generators_to_run.return_value = ['resume', 'cover_letter']
        controller.factory.get_enabled_generators.return_value = []
        controller.factory.app_config = {'cli': {'content_path_arg': 'content'}}
        controller.factory.args = {'content': 'test_resume.toml'}
        
        # Configure create_generator to return different generators
        controller.factory.create_generator.side_effect = lambda name: {
            'resume': mock_resume_generator,
            'cover_letter': mock_cover_letter_generator
        }[name]
        
        # Call method
        errors = controller.generate_documents()
        
        # Verify error was captured
        assert len(errors) == 1
        assert "Error generating resume: Resume generation failed" in errors[0]
        
        # Verify cover letter generator was still called despite resume error
        mock_cover_letter_generator.generate.assert_called_once_with(
            args=controller.factory.args, career=controller.career
        )
