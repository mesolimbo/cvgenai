"""Command-line interface for CV Gen AI."""

from typing import List, Dict, Optional

from cvgenai.controller import CVGenController


class CLI:
    """Command-line interface handler for CV Gen AI."""

    def __init__(self):
        """Initialize the CLI with a controller."""
        self.controller = CVGenController()

    @staticmethod
    def find_generator_config(generator_name: str, enabled_generators: List[Dict]) -> Optional[Dict]:
        """Find the configuration for a given generator name.

        Args:
            generator_name: The name of the generator to find.
            enabled_generators: List of enabled generator configurations.

        Returns:
            The configuration dictionary for the generator, or None if not found.
        """
        for gen in enabled_generators:
            if gen['name'] == generator_name:
                return gen

        return None


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
            generator_config = CLI.find_generator_config(generator_name, enabled_generators)
            if generator_config:
                print(f"- {generator_config['description']}")

        print(f"Using content from: {content_path}")
        print("---")

    def _prepare_and_generate(self):
        """Prepare the generation process and run it."""
        # Get generation information
        generators_to_run, enabled_generators, content_path = self.controller.get_generation_info()

        # Display what will be generated
        self.display_generation_options(generators_to_run, enabled_generators, content_path)

        # Generate documents
        return self.controller.generate_documents()

    def run(self) -> None:
        """Run the CV generation process."""
        try:
            errors = self._prepare_and_generate()

            # Display results
            if errors:
                print("\nErrors occurred during generation:")
                for error in errors:
                    print(f"- {error}")
            else:
                print("\nGeneration completed successfully!")

        except Exception as e:
            print(f"Fatal error: {e}")


if __name__ == '__main__':
    CLI().run()

