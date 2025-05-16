"""Abstract document classes for CV Generation."""

from abc import ABC, abstractmethod
import re


class Document(ABC):
    """Base class for all document types."""
    
    @abstractmethod
    def prepare_context(self, config):
        """Prepare the rendering context from configuration."""
        pass
    
    @abstractmethod
    def get_template_names(self):
        """Get the template names for this document."""
        pass
    
    @staticmethod
    def format_name_for_filename(name):
        """Convert a person's name to a filename-friendly format.
        Example: 'Jane Smith' becomes 'jane_smith'
        """
        # Replace spaces with underscores and make lowercase
        formatted_name = name.strip().lower().replace(' ', '_')
        # Remove any characters that aren't suitable for filenames
        formatted_name = re.sub(r'[^\w_]', '', formatted_name)
        return formatted_name


class ResumeDocument(Document):
    """Implementation for Resume document type."""
    
    def get_template_names(self):
        """Get the template names for resume."""
        return ['resume_page1_template.html', 'resume_page2_template.html']
    
    def prepare_context(self, config):
        """Prepare the rendering context from configuration."""
        # Extract the relevant sections from config
        resume = config.get('resume', {})
        summary_intro, summary_bullets = self._split_intro_and_bullets(resume.get('summary', ''), require_intro=True)
        highlights_bullets = self._split_intro_and_bullets(resume.get('career_highlights', ''), require_intro=False)
        
        # Prepare context for both pages
        context = {
            'personal': config.get('personal', {}),
            'resume': resume,
            'summary_intro': summary_intro,
            'summary_bullets': summary_bullets,
            'highlights_bullets': highlights_bullets,
        }
        
        return context

    @staticmethod
    def _split_intro_and_bullets(text, require_intro=True):
        """
        Split a block of text into an intro and a list of bullet points.
        If require_intro is False, treat all lines as bullets.
        """
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        if not lines:
            return ('', []) if require_intro else []
        
        if require_intro:
            intro = lines[0]
            bullets = []
            for line in lines[1:]:
                if line.startswith('- ') or line.startswith('• '):
                    bullets.append(line[2:].strip())
                else:
                    bullets.append(line)
            return intro, bullets
        else:
            bullets = []
            for line in lines:
                if line.startswith('- ') or line.startswith('• '):
                    bullets.append(line[2:].strip())
                else:
                    bullets.append(line)
            return bullets


class CoverLetterDocument(Document):
    """Implementation for Cover Letter document type."""
    
    def get_template_names(self):
        """Get the template name for cover letter."""
        return ['cover_letter_template.html']
    
    def prepare_context(self, config):
        """Prepare the rendering context from configuration."""
        context = {
            **config.get('personal', {}),
            'recipient': config.get('content', {}).get('recipient', ''),
            'content': self._format_content_as_html(config.get('content', {}).get('cover_letter', ''))
        }
        
        return context

    @staticmethod
    def _format_content_as_html(content):
        """Format cover letter content as HTML paragraphs."""
        paragraphs = content.strip().split('\n\n')
        html_content = '\n'.join(f'<p>{p.strip()}</p>' for p in paragraphs)
        return html_content
