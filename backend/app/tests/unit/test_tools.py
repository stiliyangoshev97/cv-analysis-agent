"""Unit tests for agents/tools.py functions."""

import pytest
from app.agents.tools import extract_candidate_name, validate_file


class TestExtractCandidateName:
    """Tests for extract_candidate_name function."""

    def test_extract_simple_name(self):
        """Should extract simple two-word name."""
        cv_text = """John Smith
        
        Software Engineer
        Email: john@example.com
        """
        result = extract_candidate_name(cv_text)
        assert result == "John Smith"

    def test_extract_three_word_name(self):
        """Should extract three-word name."""
        cv_text = """John William Smith
        
        Senior Developer
        """
        result = extract_candidate_name(cv_text)
        assert result == "John William Smith"

    def test_extract_cyrillic_name(self):
        """Should extract Cyrillic names correctly."""
        cv_text = """Иван Петров
        
        Разработчик программного обеспечения
        """
        result = extract_candidate_name(cv_text)
        assert result == "Иван Петров"

    def test_extract_cyrillic_three_word_name(self):
        """Should extract Cyrillic three-word name with patronymic."""
        cv_text = """Александр Сергеевич Пушкин
        
        Старший разработчик
        """
        result = extract_candidate_name(cv_text)
        assert result == "Александр Сергеевич Пушкин"

    def test_skip_resume_header(self):
        """Should skip 'Resume' header and find name."""
        cv_text = """Resume
        
        John Smith
        
        Software Engineer
        """
        result = extract_candidate_name(cv_text)
        assert result == "John Smith"

    def test_skip_cv_header(self):
        """Should skip 'CV' header and find name."""
        cv_text = """CURRICULUM VITAE
        
        Maria Garcia
        
        Data Scientist
        """
        result = extract_candidate_name(cv_text)
        assert result == "Maria Garcia"

    def test_skip_cyrillic_header(self):
        """Should skip Cyrillic 'Резюме' header and find name."""
        cv_text = """Резюме
        
        Мария Иванова
        
        Менеджер проектов
        """
        result = extract_candidate_name(cv_text)
        assert result == "Мария Иванова"

    def test_skip_email_line(self):
        """Should skip lines with email addresses."""
        cv_text = """john.smith@gmail.com
        
        John Smith
        
        Developer
        """
        result = extract_candidate_name(cv_text)
        assert result == "John Smith"

    def test_skip_phone_numbers(self):
        """Should skip lines with phone numbers."""
        cv_text = """+1 (555) 123-4567
        
        Jane Doe
        
        Engineer
        """
        result = extract_candidate_name(cv_text)
        assert result == "Jane Doe"

    def test_skip_linkedin_url(self):
        """Should skip LinkedIn URL lines."""
        cv_text = """linkedin.com/in/johndoe
        
        John Doe
        
        Software Developer
        """
        result = extract_candidate_name(cv_text)
        assert result == "John Doe"

    def test_returns_none_for_empty_text(self):
        """Should return None for empty text."""
        assert extract_candidate_name("") is None
        assert extract_candidate_name(None) is None

    def test_returns_none_for_no_valid_name(self):
        """Should return None when no valid name found."""
        cv_text = """Skills
        
        Python, JavaScript, React
        
        Experience
        """
        result = extract_candidate_name(cv_text)
        assert result is None

    def test_mixed_latin_cyrillic_name(self):
        """Should handle mixed scripts if present."""
        # This edge case tests robustness
        cv_text = """Дмитрий Kowalski
        
        Full-Stack Developer
        """
        result = extract_candidate_name(cv_text)
        # Should still extract as both words start with uppercase
        assert result == "Дмитрий Kowalski"


class TestValidateFile:
    """Tests for validate_file function."""

    def test_valid_pdf_header(self):
        """Should accept valid PDF file."""
        content = b"%PDF-1.4 some pdf content here"
        is_valid, error = validate_file(content)
        assert is_valid is True
        assert error is None

    def test_invalid_file_type(self):
        """Should reject non-PDF files."""
        content = b"<html><body>Not a PDF</body></html>"
        is_valid, error = validate_file(content)
        assert is_valid is False
        assert "Invalid file type" in error

    def test_empty_content(self):
        """Should reject empty content."""
        is_valid, error = validate_file(b"")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_file_too_large(self):
        """Should reject files over 10MB."""
        # Create a file just over 10MB
        large_content = b"%PDF-1.4" + (b"x" * (10 * 1024 * 1024 + 1))
        is_valid, error = validate_file(large_content)
        assert is_valid is False
        assert "too large" in error.lower()
