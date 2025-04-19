"""Template rendering implementations."""

from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader


class ITemplateRenderer(ABC):
    """Interface for template renderers."""
    
    @abstractmethod
    def render(self, template_name, context):
        """Render a template with the given context."""
        pass


class Jinja2Renderer(ITemplateRenderer):
    """Jinja2 implementation of the template renderer."""
    
    def __init__(self, template_dir='templates'):
        """Initialize with template directory."""
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    def render(self, template_name, context):
        """Render a template with the given context."""
        template = self.env.get_template(template_name)
        return template.render(context)
