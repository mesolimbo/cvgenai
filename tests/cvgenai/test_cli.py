"""Tests for the cli module."""

from unittest.mock import patch, MagicMock

from cvgenai.cli import CLI


class TestCLI:
    """Test cases for command-line interface functions."""

    @patch('cvgenai.cli.CVGenController')
    def test_cli_initialization(self, mock_controller_class):
        """Test CLI initialization with controller."""
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        
        cli = CLI()
        
        # Verify controller was instantiated
        mock_controller_class.assert_called_once()
        assert cli.controller == mock_controller

    @patch('cvgenai.cli.CVGenController')
    @patch('builtins.print')
    def test_cli_run_success(self, mock_print, mock_controller_class):
        """Test successful CLI run."""
        # Setup controller mock
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        
        # Setup generation info
        generators_to_run = ['resume', 'cover_letter']
        enabled_generators = [
            {'name': 'resume', 'description': 'Resume Generator'},
            {'name': 'cover_letter', 'description': 'Cover Letter Generator'}
        ]
        content_path = 'test_resume.toml'
        
        mock_controller.get_generation_info.return_value = (
            generators_to_run, enabled_generators, content_path
        )
        mock_controller.generate_documents.return_value = []  # No errors
        
        # Create and run CLI
        cli = CLI()
        cli.run()
        
        # Verify controller methods were called
        mock_controller.get_generation_info.assert_called_once()
        mock_controller.generate_documents.assert_called_once()
        
        # Verify success message was printed
        mock_print.assert_any_call("\nGeneration completed successfully!")

    @patch('cvgenai.cli.CVGenController')
    @patch('builtins.print')
    def test_cli_run_with_errors(self, mock_print, mock_controller_class):
        """Test CLI run with errors."""
        # Setup controller mock
        mock_controller = MagicMock()
        mock_controller_class.return_value = mock_controller
        
        # Setup generation info
        generators_to_run = ['resume']
        enabled_generators = [{'name': 'resume', 'description': 'Resume Generator'}]
        content_path = 'test_resume.toml'
        
        mock_controller.get_generation_info.return_value = (
            generators_to_run, enabled_generators, content_path
        )
        mock_controller.generate_documents.return_value = ['Error generating resume: Test error']
        
        # Create and run CLI
        cli = CLI()
        cli.run()
        
        # Verify error message was printed
        mock_print.assert_any_call("\nErrors occurred during generation:")
        mock_print.assert_any_call("- Error generating resume: Test error")

    @staticmethod
    @patch('cvgenai.controller.Factory')
    @patch('cvgenai.controller.Career')
    def test_display_generation_options(*_):
        """Test display of generation options."""
        generators_to_run = ['resume', 'cover_letter']
        enabled_generators = [
            {'name': 'resume', 'description': 'Resume Generator'},
            {'name': 'cover_letter', 'description': 'Cover Letter Generator'}
        ]
        content_path = 'test_resume.toml'
        
        cli = CLI()
        
        with patch('builtins.print') as mock_print:
            cli.display_generation_options(generators_to_run, enabled_generators, content_path)
            
            # Verify correct output
            mock_print.assert_any_call("Generating documents with the following options:")
            mock_print.assert_any_call("- Resume Generator")
            mock_print.assert_any_call("- Cover Letter Generator")
            mock_print.assert_any_call("Using content from: test_resume.toml")
            mock_print.assert_any_call("---")
