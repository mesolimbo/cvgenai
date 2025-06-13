"""Tests for the controller module."""

from unittest.mock import patch, MagicMock

from cvgenai.controller import CVGenController


class TestCVGenController:
    """Test cases for the CVGenController class."""

    def test_controller_initialization(self):
        """Test controller initialization."""
        controller = CVGenController()
        
        assert controller.factory is None
        assert controller.career is None

    @patch('cvgenai.controller.load_dotenv')
    @patch('cvgenai.controller.Factory')
    @patch('cvgenai.controller.Career')
    def test_initialize(self, mock_career_class, mock_factory_class, mock_load_dotenv):
        """Test controller initialization."""
        # Setup mocks
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory
        mock_factory.app_config = {'cli': {'content_path_arg': 'content'}}
        mock_factory.args = {'content': 'test_resume.toml'}
        
        mock_config_manager = MagicMock()
        mock_factory.get_service.return_value = mock_config_manager
        
        mock_career = MagicMock()
        mock_career_class.return_value = mock_career
        
        # Create and initialize controller
        controller = CVGenController()
        controller.initialize()
        
        # Verify initialization steps
        mock_load_dotenv.assert_called_once()
        mock_factory_class.assert_called_once()
        mock_career_class.assert_called_once_with(mock_config_manager)
        mock_career.load.assert_called_once_with('test_resume.toml')
        
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
        mock_factory_class.assert_called_once_with('custom_config.toml')
        assert result == mock_factory

    @patch('cvgenai.controller.Career')
    def test_initialize_career(self, mock_career_class):
        """Test career initialization."""
        # Setup controller with mock factory
        controller = CVGenController()
        controller.factory = MagicMock()
        controller.factory.app_config = {'cli': {'content_path_arg': 'content'}}
        controller.factory.args = {'content': 'test_resume.toml'}
        
        mock_config_manager = MagicMock()
        controller.factory.get_service.return_value = mock_config_manager
        
        mock_career = MagicMock()
        mock_career_class.return_value = mock_career
        
        # Call method
        result = controller._initialize_career()
        
        # Verify career initialization
        controller.factory.get_service.assert_called_once_with('config_manager')
        mock_career_class.assert_called_once_with(mock_config_manager)
        mock_career.load.assert_called_once_with('test_resume.toml')
        assert result == mock_career

    def test_get_generation_info(self):
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

    def test_generate_documents_success(self):
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

    def test_generate_documents_with_errors(self):
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
