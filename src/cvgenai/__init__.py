"""Template rendering module for CV Generation."""

from .cli import CLI

# Export a main function that creates and runs CLI for backwards compatibility
def main():
    """Main entry point for CV Generation."""
    CLI().run()

__all__ = ["main", "CLI"]
