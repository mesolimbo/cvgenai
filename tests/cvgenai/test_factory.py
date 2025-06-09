"""Tests for the factory module."""

import pytest
from unittest.mock import patch, mock_open, MagicMock
import sys

class TestFactory:
    """Test cases for the Factory class."""

    @staticmethod
    @patch('cvgenai.factory.Factory.get_service', return_value=MagicMock())
    def test_init_with_default_config(_):
        """Test initializing the factory with default config path."""
        # Patch the tomli.load function before importing Factory
        with (patch('cvgenai.config.ConfigManager.load') as mock_load,
              patch('cvgenai.factory.Factory._parse_args') as _):
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

    @staticmethod
    @patch('cvgenai.factory.Factory.get_service', return_value=MagicMock())
    def test_init_with_custom_config(_, monkeypatch):
        """Test initializing the factory with a custom config path."""
        test_args = ['cli.py']
        monkeypatch.setattr(sys, 'argv', test_args)

        with patch('cvgenai.config.ConfigManager.load') as mock_load_config:
            # Mock the _load_app_config method to return a test config
            test_config = {'test': 'config', 'documents': {'generators': []}}
            mock_load_config.return_value = test_config
            
            # Create factory with custom config path
            from cvgenai.factory import Factory
            factory = Factory('custom_config.toml')
            
            # Verify that config was loaded from custom path
            assert factory.app_config == test_config
            mock_load_config.assert_called_once_with('custom_config.toml')

    @staticmethod
    def test_load_app_config_file_exists(monkeypatch):
        """Test loading application config from an existing file."""
        test_args = ['cli.py']
        monkeypatch.setattr(sys, 'argv', test_args)

        test_config = {
            'services': {
                'test_service': 'test.module.TestClass',
                'config_manager': 'cvgenai.config.ConfigManager',
            },
            'documents': {'generators': []},
            'cli': {'args': []}
        }
        
        with (patch('builtins.open', mock_open()),
              patch('cvgenai.config.ConfigManager.load', return_value=test_config)):
            # Call the static method directly
            from cvgenai.factory import Factory
            config = Factory('test_config.toml')
            
            # Verify that config was loaded correctly
            assert config.app_config == test_config


    @staticmethod
    def test_file_not_found():
        """Test loading application config from a non-existent file."""
        with patch('cvgenai.config.ConfigManager.load', side_effect=FileNotFoundError):
            # Call the static method directly
            from cvgenai.factory import Factory

            # Verify that ValueError is raised when file does not exist
            with pytest.raises(FileNotFoundError):
                Factory('non_existent_config.toml')


    @staticmethod
    @patch('cvgenai.factory.Factory._create_instance_from_path', return_value=MagicMock())
    def test_get_service_cached(_, monkeypatch):
        """Test getting a service that is already cached."""
        test_args = ['cli.py']
        monkeypatch.setattr(sys, 'argv', test_args)

        from cvgenai.factory import Factory
        factory = Factory()
        # Manually set a cached service
        test_service = object()
        factory._service_instances = {'test_service': test_service}
        
        # Request the service
        service = factory.get_service('test_service')
        
        # Verify that the cached instance was returned
        assert service is test_service

    @patch('cvgenai.factory.Factory._create_instance_from_path', return_value=MagicMock())
    @patch('cvgenai.factory.importlib.import_module')
    def test_get_service_new(self, mock_import_module, _, monkeypatch):
        """Test getting a service that needs to be instantiated."""
        factory, mock_class, mock_instance = self.setup_mocks(mock_import_module, monkeypatch)
        factory.app_config = {
            'services': {'test_service': 'test_module.TestClass'}
        }
        
        # Get the service
        service = factory.get_service('test_service')
        
        # Verify that the service was created correctly
        assert service is mock_instance
        mock_class.assert_called_once()
        assert 'test_service' in factory._service_instances
        assert factory._service_instances['test_service'] is mock_instance

    @staticmethod
    @patch('cvgenai.factory.Factory._create_instance_from_path', return_value=MagicMock())
    def test_get_service_not_in_config(_, monkeypatch):
        """Test getting a service that is not in the config."""
        test_args = ['cli.py']
        monkeypatch.setattr(sys, 'argv', test_args)

        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {'services': {}}
        
        # Verify that requesting a non-existent service raises ValueError
        with pytest.raises(ValueError):
            factory.get_service('non_existent_service')

    @staticmethod
    @patch('cvgenai.factory.Factory._create_instance_from_path', return_value=MagicMock())
    def test_setup_argument_parser(_, monkeypatch):
        """Test setting up the argument parser with dynamic arguments."""
        test_args = ['cli.py']
        monkeypatch.setattr(sys, 'argv', test_args)

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
    @patch('cvgenai.factory.Factory._create_instance_from_path', return_value=MagicMock())
    @patch('cvgenai.factory.Factory._parse_args')
    def test_get_generators_to_run_with_flags(_, __):
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
        
        # Get generators to run
        generators = factory.get_generators_to_run()
        
        # Verify that only the specified generator is included
        assert generators == ['resume', 'cover-letter', 'other']

    @staticmethod
    @patch('cvgenai.factory.Factory._create_instance_from_path', return_value=MagicMock())
    def test_get_generators_to_run_no_flags(_, monkeypatch):
        """Test determining which generators to run when no flags are set."""
        test_args = ['cli.py']
        monkeypatch.setattr(sys, 'argv', test_args)

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

        # Get generators to run
        generators = factory.get_generators_to_run()
        
        # Verify that all enabled generators are included
        assert set(generators) == {'resume', 'cover-letter'}

    @staticmethod
    @patch('cvgenai.factory.Factory._create_instance_from_path', return_value=MagicMock())
    @patch('cvgenai.factory.Factory._create_instance_from_path', return_value=MagicMock())
    def test_create_generator(_, __, monkeypatch):
        """Test creating a document generator instance."""
        test_args = ['cli.py']
        monkeypatch.setattr(sys, 'argv', test_args)

        # Create factory with test config
        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {
            'documents': {
                'generators': [
                    {
                        'name': 'test-gen',
                        'enabled': True,
                        'class': 'cvgenai.generate.ResumeGenerator'
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
    @patch('cvgenai.factory.Factory._create_instance_from_path', return_value=MagicMock())
    def test_create_generator_not_found(_, monkeypatch):
        """Test creating a generator that doesn't exist in config."""
        test_args = ['cli.py']
        monkeypatch.setattr(sys, 'argv', test_args)

        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {
            'documents': {'generators': []}
        }
        
        # Verify that requesting a non-existent generator raises ValueError
        with pytest.raises(ValueError):
            factory.create_generator('non-existent')

    @staticmethod
    @patch('cvgenai.factory.Factory._create_instance_from_path', return_value=MagicMock())
    def test_create_generator_disabled(_, monkeypatch):
        """Test creating a generator that is disabled in config."""
        test_args = ['cli.py']
        monkeypatch.setattr(sys, 'argv', test_args)

        from cvgenai.factory import Factory
        factory = Factory()
        factory.app_config = {
            'documents': {
                'generators': [
                    {
                        'name': 'disabled-gen',
                        'enabled': False,
                        'class': 'cvgenai.generate.ResumeGenerator'
                    }
                ]
            }
        }
        
        # Verify that requesting a disabled generator raises ValueError
        with pytest.raises(ValueError):
            factory.create_generator('disabled-gen')

    @staticmethod
    @patch('cvgenai.factory.Factory._create_instance_from_path', return_value=MagicMock())
    def test_get_enabled_generators(_, monkeypatch):
        """Test getting all enabled generators from config."""
        test_args = ['cli.py']
        monkeypatch.setattr(sys, 'argv', test_args)

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
    def test_create_instance_from_path(self, mock_import_module, monkeypatch):
        """Test creating an instance from a fully-qualified class path."""
        # Setup mocks
        factory, mock_class, mock_instance = self.setup_mocks(mock_import_module, monkeypatch)

        # Create instance from path
        result = factory._create_instance_from_path('test_module.TestClass')
        
        # Verify the result
        assert result is mock_instance
        mock_import_module.assert_called_with('test_module')
        mock_class.assert_called_once()

    @staticmethod
    def setup_mocks(mock_import_module, monkeypatch):
        test_args = ['cli.py']
        monkeypatch.setattr(sys, 'argv', test_args)
        mock_class = MagicMock()
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        mock_module = MagicMock()
        mock_module.TestClass = mock_class
        mock_import_module.return_value = mock_module
        from cvgenai.factory import Factory
        factory = Factory()
        return factory, mock_class, mock_instance