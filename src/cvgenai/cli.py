"""Command-line interface for CV Gen AI."""

from typing import List, Dict

from cvgenai.controller import CVGenController


class CLI:
    """Command-line interface handler for CV Gen AI."""

    def __init__(self):
        """Initialize the CLI with a controller."""
        self.controller = CVGenController()

    @staticmethod
    def display_generation_options(generators_to_run: List[str], enabled_generators: List[Dict], content_path: str) -> None:
        """Display information about what will be generated.
        
        Args:
            generators_to_run: List of generator names that will be run
            enabled_generators: List of enabled generator configurations
            content_path: Path to the content being used
        """
        print("Generating documents with the following options:")
        for generator_name in generators_to_run:
            generator_config = next((gen for gen in enabled_generators if gen['name'] == generator_name), None)
            if generator_config:
                print(f"- {generator_config['description']}")

        print(f"Using content from: {content_path}")
        print("---")

    @staticmethod
    def display_errors(errors: List[str]) -> None:
        """Display any errors that occurred during generation.
        
        Args:
            errors: List of error messages
        """
        if errors:
            print("\nErrors occurred during generation:")
            for error in errors:
                print(f"- {error}")
        else:
            print("\nGeneration completed successfully!")

    def run(self) -> None:
        """Run the CV generation process."""
        try:
            # Initialize the controller
            self.controller.initialize()

            # Get generation information
            generators_to_run, enabled_generators, content_path = self.controller.get_generation_info()

            # Display what will be generated
            self.display_generation_options(generators_to_run, enabled_generators, content_path)

            # Generate documents
            errors = self.controller.generate_documents()

            # Display results
            self.display_errors(errors)

        except Exception as e:
            print(f"Fatal error: {e}")
            return


if __name__ == '__main__':
    cli = CLI()
    cli.run()
