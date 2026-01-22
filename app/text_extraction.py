"""
Text extraction module for various document formats.
"""

import fitz  # PyMuPDF
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os
import re
from typing import Optional, Dict, List, Tuple

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

def detect_chapters(text: str) -> List[Dict[str, any]]:
    """Detect chapters in text using regex patterns."""
    chapters = []

    # Common chapter patterns (French and English)
    patterns = [
        r'(?:^|\n|\r)\s*(?:Chapitre|Chapter|CHAPITRE|CHAPTER)\s+(\d+)(?:\s*:|\s*-|\s*\n|\s*$)',
        r'(?:^|\n|\r)\s*(?:Partie|Part|PARTIE|PART)\s+(\d+)(?:\s*:|\s*-|\s*\n|\s*$)',
        r'(?:^|\n|\r)\s*(?:Chapitre|Chapter|CHAPITRE|CHAPTER)\s+([IVXLCDM]+)(?:\s*:|\s*-|\s*\n|\s*$)',  # Roman numerals
        r'(?:^|\n|\r)\s*(\d+)\.\s*(?:Chapitre|Chapter)',
        r'(?:^|\n|\r)\s*#+\s*(?:Chapitre|Chapter|CHAPITRE|CHAPTER)\s+(\d+)',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            chapter_num = match.group(1)
            start_pos = match.start()

            # Try to find chapter title
            line_end = text.find('\n', start_pos)
            if line_end == -1:
                line_end = len(text)

            # Extract first line after chapter marker (likely the title)
            chapter_text = text[start_pos:line_end].strip()
            title_match = re.search(r'(?:Chapitre|Chapter|CHAPITRE|CHAPTER)\s+\d+\s*:?\s*(.+)', chapter_text, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else f"Chapitre {chapter_num}"

            chapters.append({
                'number': chapter_num,
                'title': title,
                'position': start_pos,
                'text_preview': chapter_text[:100] + '...' if len(chapter_text) > 100 else chapter_text
            })

    # Remove duplicates (same position)
    seen_positions = set()
    unique_chapters = []
    for chapter in chapters:
        if chapter['position'] not in seen_positions:
            seen_positions.add(chapter['position'])
            unique_chapters.append(chapter)

    # Sort by position
    unique_chapters.sort(key=lambda x: x['position'])

    return unique_chapters

def extract_text_with_metadata(file_path: str) -> Tuple[str, Dict[str, any]]:
    """Extract text and metadata from file."""
    text = extract_text(file_path)
    chapters = detect_chapters(text)

    metadata = {
        'chapters': chapters,
        'chapter_count': len(chapters),
        'text_length': len(text)
    }

    return text, metadata

def extract_text(file_path: str) -> str:
    """Extract text from file based on extension (legacy function)."""
    text, _ = extract_text_with_metadata(file_path)
    return text
