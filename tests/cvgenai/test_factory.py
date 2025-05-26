"""Tests for the factory module."""

from argparse import Namespace
import pytest
import sys
from unittest.mock import patch, mock_open, MagicMock


class TestFactory:
    """Test cases for the Factory class."""

    @staticmethod
    def test_init_with_default_config():
        """Test initializing the factory with default config path."""
        # Patch the tomli.load function before importing Factory
        with patch('cvgenai.factory.tomli.load') as mock_load:
            # Mock the tomli.load call to return a test config
            test_config = {'test': 'config'}
            mock_load.return_value = test_config
            
            # Import Factory here after patching to avoid early initialization
            from cvgenai.factory import Factory
            
            # Create factory with default config
            factory = Factory()
            
            # Verify that config was loaded properly
            assert factory.app_config == test_config
            assert factory._service_instances == {}
            assert factory.args == {}

    @staticmethod
    def test_init_with_custom_config():
        """Test initializing the factory with a custom config path."""
        with patch('cvgenai.factory.Factory._load_app_config') as mock_load_config:
            # Mock the _load_app_config method to return a test config
            test_config = {'test': 'config'}
            mock_load_config.return_value = test_config
            
            # Create factory with custom config path
            from cvgenai.factory import Factory
            factory = Factory('custom_config.toml')
            
            # Verify that config was loaded from custom path
            assert factory.app_config == test_config
            mock_load_config.assert_called_once_with('custom_config.toml')

    @staticmethod
    def test_load_app_config_file_exists():
        """Test loading application config from an existing file."""
        test_config = {
            'services': {'test_service': 'test.module.TestClass'},
            'documents': {'generators': []},
            'cli': {'args': []}
        }
        
        with patch('builtins.open', mock_open()) as mock_file, patch('cvgenai.factory.tomli.load', return_value=test_config):
            # Call the static method directly
            from cvgenai.factory import Factory
            config = Factory._load_app_config('test_config.toml')
            
            # Verify that config was loaded correctly
            assert config == test_config
            mock_file.assert_called_once_with('test_config.toml', 'rb')

    @staticmethod
    def test_load_app_config_file_not_found():
        """Test loading application config when file is not found."""
        with patch('builtins.open', side_effect=FileNotFoundError()), \
                patch('cvgenai.factory.sys.exit') as mock_exit:
            # Call the static method directly
            from cvgenai.factory import Factory
            Factory._load_app_config('non_existent_config.toml')

            # Verify sys.exit was called with code 1
            mock_exit.assert_called_once_with(1)

    @staticmethod
    def test_get_service_cached():
        """Test getting a service that is already cached."""
        from cvgenai.factory import Factory
        factory = Factory()
        # Manually set a cached service
        test_service = object()
        factory._service_instances = {'test_service': test_service}
        
        # Request the service
        service = factory.get_service('test_service')
        
        # Verify that the cached instance was returned
        assert service is test_service

    @patch('cvgenai.factory.importlib.import_module')
    def test_get_service_new(self, mock_import_module):
        """Test getting a service that needs to be instantiated."""
        # Setup mocks
        mock_class = MagicMock()
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        mock_module = MagicMock()
        mock_module.TestClass = mock_class
        mock_import_module.return_value = mock_module
        
        # Create factory with test config
        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {
            'services': {'test_service': 'test_module.TestClass'}
        }
        
        # Get the service
        service = factory.get_service('test_service')
        
        # Verify that the service was created correctly
        assert service is mock_instance
        mock_import_module.assert_called_once_with('test_module')
        mock_class.assert_called_once()
        assert 'test_service' in factory._service_instances
        assert factory._service_instances['test_service'] is mock_instance

    @staticmethod
    def test_get_service_not_in_config():
        """Test getting a service that is not in the config."""
        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {'services': {}}
        
        # Verify that requesting a non-existent service raises ValueError
        with pytest.raises(ValueError):
            factory.get_service('non_existent_service')

    @staticmethod
    def test_setup_argument_parser():
        """Test setting up the argument parser with dynamic arguments."""
        # Create factory with a test config
        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {
            'cli': {
                'content_path_arg': 'test-content',
                'content_path_default': 'test.toml',
                'content_path_help': 'Test content path',
                'args': [
                    {
                        'name': 'flag-arg',
                        'flag': True,
                        'help': 'Test flag argument',
                        'default': False
                    },
                    {
                        'name': 'value-arg',
                        'flag': False,
                        'help': 'Test value argument',
                        'default': 'default-value'
                    }
                ]
            },
            'documents': {
                'generators': [
                    {
                        'name': 'test-gen',
                        'arg': 'test-generator',
                        'arg_help': 'Test generator argument'
                    }
                ]
            }
        }
        
        # Get the argument parser
        parser = factory.setup_argument_parser()
        
        # Test parsing arguments
        args = parser.parse_args(['--test-content', 'custom.toml', 
                                  '--flag-arg', 
                                  '--value-arg', 'custom-value',
                                  '--test-generator'])
        
        # Verify that arguments were parsed correctly
        assert args.test_content == 'custom.toml'
        assert args.flag_arg is True
        assert args.value_arg == 'custom-value'
        assert args.test_generator is True

    @staticmethod
    def test_parse_args():
        """Test parsing command line arguments."""
        # Create factory and mock the argument parser
        from cvgenai.factory import Factory
        factory = Factory()
        test_args = ['--content', 'test.toml', '--html']
        expected_namespace = Namespace(content='test.toml', html=True)
        
        with patch.object(factory, 'setup_argument_parser') as mock_setup_parser:
            mock_parser = MagicMock()
            mock_parser.parse_args.return_value = expected_namespace
            mock_setup_parser.return_value = mock_parser
            
            # Parse arguments
            result = factory.parse_args(test_args)
            
            # Verify that arguments were parsed and stored
            assert result == expected_namespace
            assert factory.args == {'content': 'test.toml', 'html': True}
            mock_parser.parse_args.assert_called_once_with(test_args)

    @staticmethod
    def test_get_generators_to_run_with_flags():
        """Test determining which generators to run when specific flags are set."""
        # Create factory with test config
        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {
            'documents': {
                'generators': [
                    {
                        'name': 'resume',
                        'enabled': True,
                        'arg': 'resume'
                    },
                    {
                        'name': 'cover-letter',
                        'enabled': True,
                        'arg': 'cover-letter'
                    },
                    {
                        'name': 'other',
                        'enabled': True,
                        'arg': 'other'
                    }
                ]
            }
        }
        
        # Create args with specific generators enabled
        args = Namespace(resume=True, cover_letter=False, other=False)
        
        # Get generators to run
        generators = factory.get_generators_to_run(args)
        
        # Verify that only the specified generator is included
        assert generators == ['resume']

    @staticmethod
    def test_get_generators_to_run_no_flags():
        """Test determining which generators to run when no flags are set."""
        # Create factory with test config
        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {
            'documents': {
                'generators': [
                    {
                        'name': 'resume',
                        'enabled': True,
                        'arg': 'resume'
                    },
                    {
                        'name': 'cover-letter',
                        'enabled': True,
                        'arg': 'cover-letter'
                    }
                ]
            }
        }
        
        # Create args with no generators specifically enabled
        args = Namespace(resume=False, cover_letter=False)
        
        # Get generators to run
        generators = factory.get_generators_to_run(args)
        
        # Verify that all enabled generators are included
        assert set(generators) == {'resume', 'cover-letter'}

    @staticmethod
    def test_create_generator():
        """Test creating a document generator instance."""
        # Create factory with test config
        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {
            'documents': {
                'generators': [
                    {
                        'name': 'test-gen',
                        'enabled': True,
                        'class': 'cvgenai.resume.generate.ResumeGenerator'
                    }
                ]
            }
        }
        
        # Mock the _get_class_from_path method
        mock_generator_class = MagicMock()
        mock_generator_instance = MagicMock()
        mock_generator_class.return_value = mock_generator_instance
        
        with patch.object(factory, '_get_class_from_path', return_value=mock_generator_class):
            # Create the generator
            generator = factory.create_generator('test-gen')
            
            # Verify that the generator was created correctly
            assert generator is mock_generator_instance
            mock_generator_class.assert_called_once_with(factory=factory)

    @staticmethod
    def test_create_generator_not_found():
        """Test creating a generator that doesn't exist in config."""
        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {
            'documents': {'generators': []}
        }
        
        # Verify that requesting a non-existent generator raises ValueError
        with pytest.raises(ValueError):
            factory.create_generator('non-existent')

    @staticmethod
    def test_create_generator_disabled():
        """Test creating a generator that is disabled in config."""
        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {
            'documents': {
                'generators': [
                    {
                        'name': 'disabled-gen',
                        'enabled': False,
                        'class': 'cvgenai.resume.generate.ResumeGenerator'
                    }
                ]
            }
        }
        
        # Verify that requesting a disabled generator raises ValueError
        with pytest.raises(ValueError):
            factory.create_generator('disabled-gen')

    @staticmethod
    def test_get_enabled_generators():
        """Test getting all enabled generators from config."""
        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {
            'documents': {
                'generators': [
                    {
                        'name': 'enabled1',
                        'enabled': True
                    },
                    {
                        'name': 'enabled2'  # enabled by default
                    },
                    {
                        'name': 'disabled',
                        'enabled': False
                    }
                ]
            }
        }
        
        # Get enabled generators
        generators = factory.get_enabled_generators()
        
        # Verify that only enabled generators are returned
        assert len(generators) == 2
        assert generators[0]['name'] == 'enabled1'
        assert generators[1]['name'] == 'enabled2'

    @patch('cvgenai.factory.importlib.import_module')
    def test_get_class_from_path(self, mock_import_module):
        """Test getting a class object from its fully-qualified path."""
        # Setup mock
        mock_module = MagicMock()
        mock_class = MagicMock()
        mock_module.TestClass = mock_class
        mock_import_module.return_value = mock_module
        
        # Get class from path
        from cvgenai.factory import Factory
        result = Factory._get_class_from_path('test_module.TestClass')
        
        # Verify the result
        assert result is mock_class
        mock_import_module.assert_called_once_with('test_module')

    @patch('cvgenai.factory.importlib.import_module')
    def test_create_instance_from_path(self, mock_import_module):
        """Test creating an instance from a fully-qualified class path."""
        # Setup mocks
        mock_class = MagicMock()
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        mock_module = MagicMock()
        mock_module.TestClass = mock_class
        mock_import_module.return_value = mock_module
        
        from cvgenai.factory import Factory
        factory = Factory()
        
        # Create instance from path
        result = factory._create_instance_from_path('test_module.TestClass')
        
        # Verify the result
        assert result is mock_instance
        mock_import_module.assert_called_once_with('test_module')
        mock_class.assert_called_once()