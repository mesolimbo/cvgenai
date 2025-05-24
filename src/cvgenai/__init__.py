"""Template rendering module for CV Generation."""

from .cli import CLI

# Export the main function for backwards compatibility
main = CLI.main

__all__ = ["main", "CLI"]
