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
    
    if hasattr(args, 'html') and args.html:
        print("- HTML versions (generate_html=True)")
    else:
        print("- PDF only (generate_html=False)")
    
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
            print(f"\nGenerating {generator_name} document(s)")
            generator = factory.create_generator(generator_name)
            
            # Get HTML flag from args
            generate_html = getattr(args, 'html', False)
            
            # Generate document
            results[generator_name] = generator.generate(
                config=content_config,
                output_dir=output_dir,
                generate_html=generate_html
            )
        except Exception as e:
            print(f"Error generating {generator_name}: {e}")
            continue
    
    # Print a summary of what was generated
    print("\nGeneration completed successfully!")
    
    # Show HTML paths if requested and available
    if hasattr(args, 'html') and args.html:
        for generator_name, result in results.items():
            if 'html_paths' in result:
                for path in result['html_paths']:
                    print(f"{generator_name} HTML: {path}")
            elif 'html_path' in result and result['html_path']:
                print(f"{generator_name} HTML: {result['html_path']}")
    
    return results


if __name__ == '__main__':
    main()
