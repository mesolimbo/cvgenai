"""Factory module for creating service and generator instances."""
import importlib

import os
import argparse

from typing import Dict, Any, List, Type, TypeVar, Optional

from .config import IConfigLoader, ConfigManager


# Type variable for generic service instances
T = TypeVar('T')


class Factory:
    """Factory for creating service and generator instances based on configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize factory with application config.
        
        Args:
            config_path: Path to the application configuration file
        """
        # Allow overriding config path via environment variable
        if config_path is None:
            config_path = os.environ.get('APP_CONFIG_PATH', 'app_config.toml')

        self._config_loader: IConfigLoader = ConfigManager()
        self.app_config: Dict[str, Any] = self._config_loader.load(config_path)
        self._service_instances: Dict[str, Any] = {}
        self.args: Dict[str, Any] = self._parse_args()
        #
        # e.g.
        #
        # Here is a resume in markdown:
        # ---
        # {base_resume_md}
        # ---
        #
        # Here is a job description:
        # ---
        # {job_description}
        # ---
        #
        # Based on the job description, rewrite the resume to emphasize relevant skills and experience. Then write a personalized cover letter. Output in Markdown, clearly mark with:
        #
        # RESUME:
        # <markdown resume here>
        #
        # COVER LETTER:
        # <markdown cover letter here>
        # """
        #
        # Parse response then returne as elements
        # print(elements['config']['skills'])


    def get_service(self, service_name: str) -> Any:
        """Get a service instance by name.
        
        Args:
            service_name: Name of the service to get
            
        Returns:
            Any: Instance of the requested service
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
    

    def setup_argument_parser(self) -> argparse.ArgumentParser:
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


    def _parse_args(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Parse command-line arguments and store them in the factory.
        
        Args:
            args: Command-line arguments to parse (uses sys.argv if None)
            
        Returns:
            argparse.Namespace: Parsed arguments
        """
        parser = self.setup_argument_parser()
        parsed_args = parser.parse_args(args)
        
        return vars(parsed_args)




    def get_generators_to_run(self) -> List[str]:
        """Determine which generators to run based on arguments and configuration.
        
        Returns:
            List[str]: List of generator names to run
        """
        generators_to_run: List[str] = []
        all_generators = self.get_enabled_generators()
        
        # Check for specific generator flags in args
        any_generator_specified = False
        for generator in all_generators:
            arg_name = generator.get('arg')
            if arg_name and hasattr(self.args, arg_name.replace('-', '_')):
                arg_value = getattr(self.args, arg_name.replace('-', '_'))
                if arg_value:
                    generators_to_run.append(generator['name'])
                    any_generator_specified = True
        
        # If no specific generators were requested, run all enabled ones
        if not any_generator_specified:
            generators_to_run = [g['name'] for g in all_generators]
            
        return generators_to_run
        
    def create_generator(self, generator_name: str) -> 'Any':
        """
        Create a document generator instance by name.
        
        Args:
            generator_name: Name of the generator to create
            
        Returns:
            Any: Document generator instance
        """
        # Find generator configuration
        generator_config = None
        for gen in self.app_config['documents']['generators']:
            if gen['name'] == generator_name and gen.get('enabled', True):
                generator_config = gen
                break
                
        if not generator_config:
            raise ValueError(f"Generator '{generator_name}' not found or not enabled in configuration")
            
        # Get the generator class path and instantiate it with the factory
        class_path = generator_config['class']
        generator_class = self._get_class_from_path(class_path)
        
        # Create and return the generator instance with factory injected
        return generator_class(factory=self)
        
    def get_enabled_generators(self) -> List[Dict[str, Any]]:
        """Get a list of all enabled generators from configuration.
        
        Returns:
            List[Dict[str, Any]]: List of generator configurations
        """
        return [gen for gen in self.app_config['documents']['generators'] 
                if gen.get('enabled', True)]

    @staticmethod
    def _get_class_from_path(class_path: str) -> Type[Any]:
        """Get a class object from its fully-qualified path.
        
        Args:
            class_path: String with module path and class name
            
        Returns:
            Type[Any]: The class object
        """
        module_path, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
        
    def _create_instance_from_path(self, class_path: str) -> Any:
        """Instantiate a class from its fully-qualified path.
        
        Args:
            class_path: String with module path and class name
            
        Returns:
            Any: Instance of the specified class
        """
        cls = self._get_class_from_path(class_path)
        return cls()