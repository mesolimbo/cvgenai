"""Tests for the templating.renderer module."""

import pytest
import tempfile
from pathlib import Path
from cvgenai.templating.renderer import ITemplateRenderer, Jinja2Renderer


class TestITemplateRenderer:
    """Test cases for the ITemplateRenderer interface."""

    @staticmethod
    def test_cannot_instantiate_abstract_class():
        """Test that ITemplateRenderer cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ITemplateRenderer()


class TestJinja2Renderer:
    """Test cases for the Jinja2Renderer implementation."""

    def setup_method(self):
        """Set up test environment before each test method."""
        # Create a temporary directory for templates
        self.template_dir = tempfile.TemporaryDirectory()
        
        # Create a simple test template
        simple_template_path = Path(self.template_dir.name) / "simple.html"
        with open(simple_template_path, 'w') as f:
            f.write("<h1>Hello, {{ name }}!</h1>")
        
        # Create a template that extends another template
        base_template_path = Path(self.template_dir.name) / "base.html"
        with open(base_template_path, 'w') as f:
            f.write("<!DOCTYPE html>\n<html>\n<body>{% block content %}{% endblock %}</body>\n</html>")
            
        child_template_path = Path(self.template_dir.name) / "child.html"
        with open(child_template_path, 'w') as f:
            f.write("{% extends 'base.html' %}\n{% block content %}<p>{{ message }}</p>{% endblock %}")

        # Initialize the renderer with our temporary template directory
        self.renderer = Jinja2Renderer(self.template_dir.name)

    def teardown_method(self):
        """Clean up after each test method."""
        self.template_dir.cleanup()

    @staticmethod
    def test_init_with_default_template_dir():
        """Test initialization with default template directory."""
        renderer = Jinja2Renderer()
        assert renderer.env.loader.searchpath == ['templates']

    @staticmethod
    def test_init_with_custom_template_dir():
        """Test initialization with a custom template directory."""
        custom_dir = 'custom/templates'
        renderer = Jinja2Renderer(custom_dir)
        assert renderer.env.loader.searchpath == [custom_dir]

    def test_render_simple_template(self):
        """Test rendering a simple template with context."""
        result = self.renderer.render('simple.html', {'name': 'World'})
        assert result == "<h1>Hello, World!</h1>"

    def test_render_with_empty_context(self):
        """Test rendering with an empty context."""
        # Create a template that doesn't require context
        no_context_path = Path(self.template_dir.name) / "no_context.html"
        with open(no_context_path, 'w') as f:
            f.write("<p>Static content</p>")
            
        result = self.renderer.render('no_context.html', {})
        assert result == "<p>Static content</p>"

    def test_render_with_template_inheritance(self):
        """Test rendering a template that extends another template."""
        result = self.renderer.render('child.html', {'message': 'Template inheritance works!'})
        expected = "<!DOCTYPE html>\n<html>\n<body><p>Template inheritance works!</p></body>\n</html>"
        assert result == expected

    def test_template_not_found(self):
        """Test handling of non-existent templates."""
        with pytest.raises(Exception):
            self.renderer.render('non_existent.html', {})