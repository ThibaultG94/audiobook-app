"""
Text extraction module for various document formats.
"""

import fitz  # PyMuPDF
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os
from typing import Optional

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file using PyMuPDF."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"File is not a PDF: {file_path}")
        
        doc = fitz.open(file_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            text += page_text + "\n"
        
        doc.close()
        return text.strip()
    
    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF {file_path}: {str(e)}")

def extract_text_from_epub(file_path: str) -> str:
    """Extract text from EPUB file using ebooklib."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"EPUB file not found: {file_path}")
        
        if not file_path.lower().endswith('.epub'):
            raise ValueError(f"File is not an EPUB: {file_path}")
        
        book = epub.read_epub(file_path)
        text = ""
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                # Get text
                page_text = soup.get_text()
                text += page_text + "\n"
        
        return text.strip()
    
    except Exception as e:
        raise RuntimeError(f"Error extracting text from EPUB {file_path}: {str(e)}")

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"TXT file not found: {file_path}")
        
        if not file_path.lower().endswith('.txt'):
            raise ValueError(f"File is not a TXT: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Error reading TXT file {file_path}: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error extracting text from TXT {file_path}: {str(e)}")

def extract_text(file_path: str) -> str:
    """Extract text from file based on extension."""
    if not file_path or not isinstance(file_path, str):
        raise ValueError("Invalid file path")
    
    file_path = file_path.strip()
    
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.epub'):
        return extract_text_from_epub(file_path)
    elif file_path.lower().endswith('.txt'):
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}. Supported formats: PDF, EPUB, TXT")
