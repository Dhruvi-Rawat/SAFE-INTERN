# intake/input_router.py
"""
Routes user input to the correct extractor
and returns raw text for intake processing.

Supported input types:
- Plain text
- PDF files
- URLs

Purpose:
- Centralized input routing
- Minimal validation
- Basic normalization only
"""

from typing import Optional, Tuple, Dict

from utils.pdf_parser import extract_text_from_pdf     # PDF extraction
from utils.url_fetcher import fetch_text_from_url      # URL content fetch
from utils.text_cleaner import basic_clean_text        # Minimal cleaning


MAX_TEXT_LENGTH = 50000  # safety limit


def route_input(
    text_input: Optional[str] = None,
    pdf_file: Optional[bytes] = None,
    url: Optional[str] = None,
    return_metadata: bool = False
) -> str | Tuple[str, Dict]:
    """
    Determine input type and extract raw text.

    Args:
        text_input: Direct text entered by user
        pdf_file: Uploaded PDF file (bytes)
        url: URL provided by user
        return_metadata: If True, return (text, metadata)

    Returns:
        Cleaned text OR (cleaned text, metadata)

    Raises:
        ValueError: If no valid input is provided
    """

    raw_text = ""
    metadata = {}

    # ---------- TEXT INPUT ----------
    if text_input and text_input.strip():
        raw_text = text_input.strip()
        metadata["input_type"] = "text"

        if len(raw_text) > MAX_TEXT_LENGTH:
            raise ValueError("Text input too long")

    # ---------- PDF INPUT ----------
    elif pdf_file:
        raw_text = extract_text_from_pdf(pdf_file)
        metadata["input_type"] = "pdf"
        metadata["file_size_bytes"] = len(pdf_file)

    # ---------- URL INPUT ----------
    elif url and url.strip():
        raw_text = fetch_text_from_url(url.strip())
        metadata["input_type"] = "url"
        metadata["url"] = url.strip()

    else:
        raise ValueError("No valid input provided")

    # ---------- BASIC CLEANING ----------
    # This is NOT NLP cleaning, only normalization
    clean_text = basic_clean_text(raw_text)

    if return_metadata:
        metadata["text_length"] = len(clean_text)
        return clean_text, metadata

    return clean_text
