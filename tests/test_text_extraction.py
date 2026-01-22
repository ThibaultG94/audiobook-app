"""
Unit tests for text extraction module.
"""

import pytest
import os
import tempfile
from app.text_extraction import extract_text_from_txt, extract_text

def test_extract_text_from_txt():
    """Test TXT extraction."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello World\nThis is a test.")
        temp_path = f.name
    
    try:
        result = extract_text_from_txt(temp_path)
        assert result == "Hello World\nThis is a test."
    finally:
        os.unlink(temp_path)

def test_extract_text_invalid_file():
    """Test error handling for invalid file."""
    with pytest.raises(RuntimeError):
        extract_text("nonexistent.txt")
    
    with pytest.raises(ValueError):
        extract_text("invalid.xyz")

def test_extract_text_empty_path():
    """Test error handling for empty path."""
    with pytest.raises(ValueError):
        extract_text("")

# TODO: Add tests for PDF and EPUB when sample files are available
