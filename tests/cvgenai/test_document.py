"""Tests for the Document classes in document module."""

from cvgenai.document import Document, ResumeDocument, CoverLetterDocument


class TestDocument:
    """Test cases for the Document base class."""

    @staticmethod
    def test_format_name_for_filename():
        """Test converting a person's name to filename-friendly format."""
        # Test basic conversion with spaces
        assert Document.format_name_for_filename("Jane Smith") == "jane_smith"
        
        # Test with leading/trailing spaces
        assert Document.format_name_for_filename("  John Doe  ") == "john_doe"
        
        # Test with special characters
        assert Document.format_name_for_filename("Alex O'Brien-Jones") == "alex_obrienjones"
        
        # Test with numbers (should be preserved)
        assert Document.format_name_for_filename("User 123") == "user_123"


class TestResumeDocument:
    """Test cases for the ResumeDocument class."""
    
    @staticmethod
    def test_get_template_names():
        """Test that correct template names are returned."""
        document = ResumeDocument()
        templates = document.get_template_names()
        
        assert isinstance(templates, list)
        assert len(templates) == 2
        assert templates[0] == "resume_page1_template.html"
        assert templates[1] == "resume_page2_template.html"
    
    @staticmethod
    def test_split_intro_and_bullets_with_intro_required():
        """Test the helper method that splits text into intro and bullets."""
        document = ResumeDocument()
        
        # Test with intro and bullets
        text = "This is the introduction.\n- Point one\n- Point two\nPoint three"
        intro, bullets = document._split_intro_and_bullets(text, require_intro=True)
        
        assert intro == "This is the introduction."
        assert bullets == ["Point one", "Point two", "Point three"]
        
        # Test with only intro
        text = "This is only an introduction."
        intro, bullets = document._split_intro_and_bullets(text, require_intro=True)
        
        assert intro == "This is only an introduction."
        assert bullets == []
        
        # Test with empty string
        intro, bullets = document._split_intro_and_bullets("", require_intro=True)
        
        assert intro == ""
        assert bullets == []
    
    @staticmethod
    def test_split_intro_and_bullets_without_intro():
        """Test the helper method when intro is not required."""
        document = ResumeDocument()
        
        # Test with bullets
        text = "- Point one\n- Point two\nPoint three"
        bullets = document._split_intro_and_bullets(text, require_intro=False)
        
        assert bullets == ["Point one", "Point two", "Point three"]
        
        # Test with empty string
        bullets = document._split_intro_and_bullets("", require_intro=False)
        
        assert bullets == []

    @staticmethod
    def test_prepare_context():
        """Test preparation of the rendering context from config."""
        document = ResumeDocument()
        
        # Prepare a sample config
        config = {
            "personal": {
                "name": "Jane Smith",
                "email": "jane@example.com"
            },
            "resume": {
                "summary": "Professional software engineer.\n- 10+ years experience\n- Python expert",
                "career_highlights": "- Led multiple projects\n- Improved system performance by 50%"
            }
        }
        
        context = document.prepare_context(config)
        
        # Check the context has the required keys
        assert "personal" in context
        assert "resume" in context
        assert "summary_intro" in context
        assert "summary_bullets" in context
        assert "highlights_bullets" in context
        
        # Check the values
        assert context["personal"]["name"] == "Jane Smith"
        assert context["summary_intro"] == "Professional software engineer."
        assert "10+ years experience" in context["summary_bullets"]
        assert "Led multiple projects" in context["highlights_bullets"]


class TestCoverLetterDocument:
    """Test cases for the CoverLetterDocument class."""
    
    @staticmethod
    def test_get_template_names():
        """Test that correct template names are returned."""
        document = CoverLetterDocument()
        templates = document.get_template_names()
        
        assert isinstance(templates, list)
        assert len(templates) == 1
        assert templates[0] == "cover_letter_template.html"
    
    @staticmethod
    def test_format_content_as_html():
        """Test converting plain text to HTML paragraphs."""
        document = CoverLetterDocument()
        
        # Test with multiple paragraphs
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        html = document._format_content_as_html(text)
        
        assert html == "<p>First paragraph.</p>\n<p>Second paragraph.</p>\n<p>Third paragraph.</p>"
        
        # Test with single paragraph
        text = "Only one paragraph."
        html = document._format_content_as_html(text)
        
        assert html == "<p>Only one paragraph.</p>"
        
        # Test with empty string
        html = document._format_content_as_html("")
        
        assert html == "<p></p>"  # The method wraps even an empty string in <p> tags

    @staticmethod
    def test_prepare_context():
        """Test preparation of the rendering context from config."""
        document = CoverLetterDocument()
        
        # Prepare a sample config
        config = {
            "personal": {
                "name": "Jane Smith",
                "email": "jane@example.com"
            },
            "letter": {
                "recipient": "HR Department",
                "letter_body": "Dear HR,\n\nI am writing to apply for the position."
            }
        }
        
        context = document.prepare_context(config)
        
        # Check the context has the required keys and values
        assert context["name"] == "Jane Smith"
        assert context["email"] == "jane@example.com"
        assert context["recipient"] == "HR Department"
        assert "<p>Dear HR,</p>" in context["content"]
        assert "<p>I am writing to apply for the position.</p>" in context["content"]