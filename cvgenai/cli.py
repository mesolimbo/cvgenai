"""Command-line interface for CV Gen AI."""

import argparse
from pathlib import Path
import sys

from .config import ConfigManager
from .templating import Jinja2Renderer
from .services.pdf_service import PDFService
from .services.html_service import HTMLService
from .services.file_service import FileService
from .resume import ResumeGenerator, CoverLetterGenerator


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate resume and/or cover letter')
    parser.add_argument('--resume', action='store_true', help='Generate resume')
    parser.add_argument('--cover-letter', action='store_true', help='Generate cover letter')
    parser.add_argument('--html', action='store_true', help='Generate HTML versions of files')
    parser.add_argument('--content', default='resume.toml', help='Path to the resume content file')
    return parser.parse_args()


def main():
    """Parse command line arguments and run document generation."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Default to generating both if no specific option is selected
    if not args.resume and not args.cover_letter:
        args.resume = True
        args.cover_letter = True
    
    # Print a message about what's being generated
    print("Generating documents with the following options:")
    if args.resume:
        print("- Resume")
    if args.cover_letter:
        print("- Cover Letter")
    if args.html:
        print("- HTML versions (generate_html=True)")
    else:
        print("- PDF only (generate_html=False)")
    print(f"Using configuration from: {args.content}")
    print("---")
    
    # Initialize services using dependency injection pattern
    config_manager = ConfigManager()
    renderer = Jinja2Renderer()
    pdf_service = PDFService()
    html_service = HTMLService()
    file_service = FileService()
    
    # Load configuration
    try:
        config = config_manager.load(args.content)
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.content}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = file_service.ensure_directory('output')
    
    # Generate requested documents
    results = {}
    
    if args.resume:
        print(f"\nCreating resume generator with generate_html={args.html}")
        resume_generator = ResumeGenerator(
            renderer=renderer, 
            pdf_service=pdf_service,
            html_service=html_service,
            file_service=file_service
        )
        results['resume'] = resume_generator.generate(
            config=config, 
            output_dir=output_dir, 
            generate_html=args.html
        )
    
    if args.cover_letter:
        print(f"\nCreating cover letter generator with generate_html={args.html}")
        cover_letter_generator = CoverLetterGenerator(
            renderer=renderer, 
            pdf_service=pdf_service,
            html_service=html_service,
            file_service=file_service
        )
        results['cover_letter'] = cover_letter_generator.generate(
            config=config, 
            output_dir=output_dir, 
            generate_html=args.html
        )
    
    # Print a summary of what was generated
    print("\nGeneration completed successfully!")
    if args.resume and args.html and 'resume' in results:
        html_paths = results['resume'].get('html_paths', [])
        if html_paths:
            for path in html_paths:
                print(f"Resume HTML: {path}")
    
    if args.cover_letter and args.html and 'cover_letter' in results:
        html_path = results['cover_letter'].get('html_path')
        if html_path:
            print(f"Cover Letter HTML: {html_path}")
    
    return results
