"""Command-line interface for CV Gen AI."""

import os
from typing import List, Any, Dict

from dotenv import load_dotenv

from cvgenai.factory import Factory
from cvgenai.generate import IDocumentGenerator


class CLI:
    """Command-line interface handler for CV Gen AI."""

    @staticmethod
    def initialize_factory() -> Factory:
        """Initialize factory with configuration."""
        config_path = os.environ.get('APP_CONFIG_PATH', 'app_config.toml')
        return Factory(config_path)


    @staticmethod
    def display_generation_options(generators_to_run: List[str], enabled_generators: List[Dict], args: Any, factory: Factory) -> None:
        """Display information about what will be generated."""
        print("Generating documents with the following options:")
        for generator_name in generators_to_run:
            generator_config = next((gen for gen in enabled_generators if gen['name'] == generator_name), None)
            if generator_config:
                print(f"- {generator_config['description']}")

        # Get content path from args just for display purpose
        content_arg = factory.app_config.get('cli', {}).get('content_path_arg', 'content')
        content_path = getattr(args, content_arg)
        print(f"Using content from: {content_path}")
        print("---")


    @staticmethod
    def run_generators(generators_to_run: List[str], factory: Factory, args: Any) -> None:
        """Run the specified document generators."""
        for generator_name in generators_to_run:
            try:
                # Create generator instance from factory
                generator: IDocumentGenerator = factory.create_generator(generator_name)

                # Let the generator use the factory to get what it needs
                generator.generate(args=args)
            except Exception as e:
                print(f"Error generating {generator_name}: {e}")
                continue

        # Print a summary of what was generated
        print("\nGeneration completed successfully!")


    @staticmethod
    def main() -> None:
        """Parse command line arguments and run document generation."""
        # Load API key as environment variables from .env file
        load_dotenv()

        # Initialize factory
        factory = CLI.initialize_factory()

        # Parse arguments and store them in the factory
        args = factory.parse_args()

        # Determine which generators to run based on args and config
        generators_to_run: List[str] = factory.get_generators_to_run(args)
        enabled_generators = factory.get_enabled_generators()

        # Display generation options
        CLI.display_generation_options(generators_to_run, enabled_generators, args, factory)

        # Generate requested documents
        CLI.run_generators(generators_to_run, factory, args)


if __name__ == '__main__':
    CLI.main()
