"""Factory module for creating service and generator instances."""

import importlib
import tomli
import os
from pathlib import Path
import argparse


class Factory:
    """Factory for creating service and generator instances based on configuration."""
    
    def __init__(self, config_path=None):
        """Initialize factory with application config.
        
        Args:
            config_path: Path to the application configuration file
        """
        # Allow overriding config path via environment variable
        if config_path is None:
            config_path = os.environ.get('APP_CONFIG_PATH', 'app_config.toml')
            
        self.app_config = self._load_app_config(config_path)
        self._service_instances = {}
        
    def _load_app_config(self, config_path):
        """Load application configuration from TOML file.
        
        Args:
            config_path: Path to the application configuration file
            
        Returns:
            dict: Loaded configuration
        """
        try:
            with open(config_path, 'rb') as f:
                return tomli.load(f)
        except FileNotFoundError:
            # If the custom app config is not found, return a default configuration
            return {
                'services': {
                    'config_manager': 'config.toml.ConfigManager',
                    'template_renderer': 'templating.renderer.Jinja2Renderer',
                    'pdf_service': 'services.pdf_service.PDFService',
                    'html_service': 'services.html_service.HTMLService',
                    'file_service': 'services.file_service.FileService',
                },
                'documents': {
                    'generators': [
                        {
                            'name': 'resume',
                            'enabled': True,
                            'class': 'resume.generate.ResumeGenerator',
                            'description': 'Resume document generator',
                            'arg': 'resume',
                            'arg_help': 'Generate resume'
                        },
                        {
                            'name': 'cover_letter',
                            'enabled': True,
                            'class': 'resume.generate.CoverLetterGenerator',
                            'description': 'Cover Letter document generator',
                            'arg': 'cover-letter',
                            'arg_help': 'Generate cover letter'
                        }
                    ]
                },
                'cli': {
                    'content_path_arg': 'content',
                    'content_path_default': 'resume.toml',
                    'content_path_help': 'Path to the resume content file',
                    'args': [
                        {
                            'name': 'html',
                            'flag': True,
                            'help': 'Generate HTML versions of files',
                            'default': False
                        }
                    ]
                }
            }
            
    def get_service(self, service_name):
        """Get a service instance by name.
        
        Args:
            service_name: Name of the service to get
            
        Returns:
            object: Instance of the requested service
        """
        # Return cached instance if available
        if service_name in self._service_instances:
            return self._service_instances[service_name]
            
        # Get class path from config
        if service_name not in self.app_config['services']:
            raise ValueError(f"Service '{service_name}' not found in configuration")
            
        class_path = self.app_config['services'][service_name]
        
        # Dynamically import and instantiate the class
        service_instance = self._create_instance_from_path(class_path)
        
        # Cache the instance
        self._service_instances[service_name] = service_instance
        
        return service_instance
    
    def setup_argument_parser(self):
        """Create an argument parser with dynamically configured arguments.
        
        Returns:
            argparse.ArgumentParser: Configured argument parser
        """
        parser = argparse.ArgumentParser(description='Generate documents based on configuration')
        
        # Add content path argument
        cli_config = self.app_config.get('cli', {})
        parser.add_argument(
            f"--{cli_config.get('content_path_arg', 'content')}", 
            default=cli_config.get('content_path_default', 'resume.toml'),
            help=cli_config.get('content_path_help', 'Path to the content file')
        )
        
        # Add global arguments
        for arg_config in cli_config.get('args', []):
            arg_name = arg_config.get('name')
            if not arg_name:
                continue
                
            if arg_config.get('flag', False):
                parser.add_argument(
                    f"--{arg_name}", 
                    action='store_true',
                    default=arg_config.get('default', False),
                    help=arg_config.get('help', '')
                )
            else:
                parser.add_argument(
                    f"--{arg_name}",
                    default=arg_config.get('default'),
                    help=arg_config.get('help', '')
                )
        
        # Add generator-specific arguments
        for generator in self.app_config['documents']['generators']:
            if 'arg' in generator:
                parser.add_argument(
                    f"--{generator['arg']}",
                    action='store_true',
                    help=generator.get('arg_help', generator.get('description', ''))
                )
        
        return parser
    
    def get_generators_to_run(self, args):
        """Determine which generators to run based on arguments and configuration.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            list: List of generator names to run
        """
        generators_to_run = []
        all_generators = self.get_enabled_generators()
        
        # Check for specific generator flags in args
        any_generator_specified = False
        for generator in all_generators:
            arg_name = generator.get('arg')
            if arg_name and hasattr(args, arg_name.replace('-', '_')):
                arg_value = getattr(args, arg_name.replace('-', '_'))
                if arg_value:
                    generators_to_run.append(generator['name'])
                    any_generator_specified = True
        
        # If no specific generators were requested, run all enabled ones
        if not any_generator_specified:
            generators_to_run = [g['name'] for g in all_generators]
            
        return generators_to_run
        
    def create_generator(self, generator_name):
        """Create a document generator instance by name.
        
        Args:
            generator_name: Name of the generator to create
            
        Returns:
            object: Instance of the requested generator
        """
        # Find generator configuration
        generator_config = None
        for gen in self.app_config['documents']['generators']:
            if gen['name'] == generator_name and gen.get('enabled', True):
                generator_config = gen
                break
                
        if not generator_config:
            raise ValueError(f"Generator '{generator_name}' not found or not enabled in configuration")
            
        # Get the generator class
        class_path = generator_config['class']
        
        # Get all required services for the generator
        template_renderer = self.get_service('template_renderer')
        pdf_service = self.get_service('pdf_service')
        html_service = self.get_service('html_service')
        file_service = self.get_service('file_service')
        
        # Create and return the generator instance with dependencies injected
        generator_class = self._get_class_from_path(class_path)
        return generator_class(
            renderer=template_renderer,
            pdf_service=pdf_service,
            html_service=html_service,
            file_service=file_service
        )
        
    def get_enabled_generators(self):
        """Get a list of all enabled generators from configuration.
        
        Returns:
            list: List of generator configurations
        """
        return [gen for gen in self.app_config['documents']['generators'] 
                if gen.get('enabled', True)]
        
    def _get_class_from_path(self, class_path):
        """Get a class object from its fully-qualified path.
        
        Args:
            class_path: String with module path and class name
            
        Returns:
            class: The class object
        """
        module_path, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
        
    def _create_instance_from_path(self, class_path):
        """Instantiate a class from its fully-qualified path.
        
        Args:
            class_path: String with module path and class name
            
        Returns:
            object: Instance of the specified class
        """
        cls = self._get_class_from_path(class_path)
        return cls()