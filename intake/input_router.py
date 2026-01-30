# intake/input_router.py
"""
Routes user input to the correct extractor
and returns raw text for intake processing.

Supported input types:
- Plain text
- PDF files
- URLs
"""

from typing import Optional, Tuple, Dict

from utils.pdf_parser import extract_text_from_pdf
from utils.url_fetcher import fetch_text_from_url
from utils.text_cleaner import basic_clean_text


MAX_TEXT_LENGTH = 50000


def route_input(
    text_input: Optional[str] = None,
    pdf_file: Optional[bytes] = None,
    url: Optional[str] = None,
    return_metadata: bool = False
) -> str | Tuple[str, Dict]:

    raw_text = ""
    metadata = {}

    if text_input and text_input.strip():
        raw_text = text_input.strip()
        metadata["input_type"] = "text"

        if len(raw_text) > MAX_TEXT_LENGTH:
            raise ValueError("Text input too long")

    elif pdf_file:
        raw_text = extract_text_from_pdf(pdf_file)
        metadata["input_type"] = "pdf"
        metadata["file_size_bytes"] = len(pdf_file)

    elif url and url.strip():
        raw_text = fetch_text_from_url(url.strip())
        metadata["input_type"] = "url"
        metadata["url"] = url.strip()

    else:
        raise ValueError("No valid input provided")

    clean_text = basic_clean_text(raw_text)

    if return_metadata:
        metadata["text_length"] = len(clean_text)
        return clean_text, metadata

    return clean_text
