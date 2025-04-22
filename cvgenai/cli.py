"""Command-line interface for CV Gen AI."""

import sys
import os

from factory import Factory


def main():
    """Parse command line arguments and run document generation."""
    # Initialize factory with app config from environment or default path
    config_path = os.environ.get('APP_CONFIG_PATH', 'app_config.toml')
    factory = Factory(config_path)
    
    # Set up argument parser from configuration
    parser = factory.setup_argument_parser()
    args = parser.parse_args()
    
    # Determine which generators to run based on args and config
    generators_to_run = factory.get_generators_to_run(args)
    enabled_generators = factory.get_enabled_generators()
    
    # Print a message about what's being generated
    print("Generating documents with the following options:")
    for generator_name in generators_to_run:
        generator_config = next((gen for gen in enabled_generators if gen['name'] == generator_name), None)
        if generator_config:
            print(f"- {generator_config['description']}")
    
    # Get content path from args (using the dynamic name from config)
    content_arg = factory.app_config.get('cli', {}).get('content_path_arg', 'content')
    content_path = getattr(args, content_arg)
    print(f"Using content from: {content_path}")
    print("---")
    
    # Load content configuration
    config_manager = factory.get_service('config_manager')
    try:
        content_config = config_manager.load(content_path)
    except FileNotFoundError:
        print(f"Error: Configuration file '{content_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    file_service = factory.get_service('file_service')
    output_dir = file_service.ensure_directory('output')
    
    # Generate requested documents
    results = {}
    
    for generator_name in generators_to_run:
        try:
            # Create generator instance from factory
            generator = factory.create_generator(generator_name)
            
            # Generate document - pass args directly to the generator
            results[generator_name] = generator.generate(
                config=content_config,
                output_dir=output_dir,
                args=args
            )
        except Exception as e:
            print(f"Error generating {generator_name}: {e}")
            continue
    
    # Print a summary of what was generated
    print("\nGeneration completed successfully!")
    
    return results


if __name__ == '__main__':
    main()
