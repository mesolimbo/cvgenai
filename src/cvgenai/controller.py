"""Controller module for CV Gen AI business logic."""
import os
from typing import List, Dict, Tuple

from cvgenai.factory import Factory
from cvgenai.generate import IDocumentGenerator
from cvgenai.career import Career

class CVGenController:
    """Controller class that handles the core business logic for CV generation."""

    def __init__(self):
        """Initialize the controller with factory and career data."""
        self.factory = self._initialize_factory()
        self.career = self._initialize_career()

    @staticmethod
    def _initialize_factory() -> Factory:
        """Initialize factory with configuration.
        
        Returns:
            Factory: Initialized factory instance
        """
        config_path = os.environ.get('APP_CONFIG_PATH', 'app_config.toml')
        return Factory(config_path)

    def _initialize_career(self) -> Career:
        """Initialize and load career data.

        Returns:
            Career: Initialized career instance with loaded data
        """
        # Get services from the factory
        config_manager = self.factory.get_service('config_manager')
        file_service = self.factory.get_service('file_service')
        customizer = self.factory.get_service('customizer_service')

        # Create career instance with config manager
        career = Career(config_manager)

        # Get content path from args
        content_arg = self.factory.app_config.get('cli', {}).get('content_path_arg', 'content')
        content_path = self.factory.args[content_arg]

        # Load job description if provided and within the project root
        job_path = self.factory.args.get('job')
        job_description = ''
        if job_path:
            try:
                job_description = file_service.safe_read(job_path)
            except (FileNotFoundError, ValueError):
                job_description = ''

        customize_lambda = (lambda content: customizer.customize(content, job_description)) if job_description else None
        resume_text = file_service.safe_read(content_path)
        career.load(resume_text, customize_lambda)
        
        return career

    def get_generation_info(self) -> Tuple[List[str], List[Dict], str]:
        """Get information about what will be generated.

        Returns:
            Tuple containing:
            - List of generator names to run
            - List of enabled generators config
            - Content path being used
        """
        generators_to_run = self.factory.get_generators_to_run()
        enabled_generators = self.factory.get_enabled_generators()
        
        # Get content path for display purposes
        content_arg = self.factory.app_config.get('cli', {}).get('content_path_arg', 'content')
        content_path = self.factory.args[content_arg]
        
        return generators_to_run, enabled_generators, content_path

    def generate_documents(self) -> List[str]:
        """Generate the requested documents.

        Returns:
            List of any error messages that occurred during generation
        """
        generators_to_run, _, _ = self.get_generation_info()
        errors = []
        
        for generator_name in generators_to_run:
            try:
                # Create generator instance from factory
                generator: IDocumentGenerator = self.factory.create_generator(generator_name)

                # Let the generator use the factory and career to get what it needs
                generator.generate(args=self.factory.args, career=self.career)
            except Exception as e:
                error_msg = f"Error generating {generator_name}: {e}"
                errors.append(error_msg)
                continue

        return errors
