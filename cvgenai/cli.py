"""Command-line interface for CV Gen AI."""

import os
from typing import List

from factory import Factory
from resume.generate import IDocumentGenerator


def main() -> None:
    """Parse command line arguments and run document generation."""
    # Initialize factory with app config from environment or default path
    config_path = os.environ.get('APP_CONFIG_PATH', 'app_config.toml')
    factory = Factory(config_path)
    
    # Parse arguments and store them in the factory
    args = factory.parse_args()
    
    # Determine which generators to run based on args and config
    generators_to_run: List[str] = factory.get_generators_to_run(args)
    enabled_generators = factory.get_enabled_generators()
    
    # Print a message about what's being generated
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
    
    # Generate requested documents
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


if __name__ == '__main__':
    main()
