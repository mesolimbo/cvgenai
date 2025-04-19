"""Main entry point for CV Gen AI."""

import argparse
from pathlib import Path

from .config import load_config
from .resume.generate import generate_resume, generate_cover_letter


def main():
    """Parse command line arguments and run document generation."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate resume and/or cover letter')
    parser.add_argument('--resume', action='store_true', help='Generate resume')
    parser.add_argument('--cover-letter', action='store_true', help='Generate cover letter')
    parser.add_argument('--html', action='store_true', help='Generate HTML versions of files')
    parser.add_argument('--config', default='config.toml', help='Path to the config file')
    args = parser.parse_args()
    
    # Default to generating both if no specific option is selected
    if not args.resume and not args.cover_letter:
        args.resume = True
        args.cover_letter = True
    
    # Load configuration
    config = load_config(args.config)
    
    # Create output directory if it doesn't exist
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Generate requested documents
    results = {}
    
    if args.resume:
        results['resume'] = generate_resume(config, output_dir, generate_html=args.html)
    
    if args.cover_letter:
        results['cover_letter'] = generate_cover_letter(config, output_dir, generate_html=args.html)
    
    return results


if __name__ == '__main__':
    main()
