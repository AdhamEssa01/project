"""
Unified file-to-text extraction for supported upload types.

Only PDF is supported. Any other file type raises a ValueError so the
batch screening service can isolate the error per file.
"""

from __future__ import annotations

import os
from io import BytesIO

from fastapi import UploadFile

from app.config import SUPPORTED_EXTENSIONS, MIN_RESUME_TEXT_LENGTH
from app.pdf_utils import extract_text_advanced


def _extension(filename: str) -> str:
    """Return the lowercase file extension including the dot."""
    _, ext = os.path.splitext(filename or "")
    return ext.lower()


async def extract_text_from_upload(file: UploadFile) -> str:
    """
    Read an uploaded file and return its plain text content.

    Raises:
        ValueError: if the file type is unsupported, the file is empty,
                    or the extracted text is too short to be useful.
    """
    ext = _extension(file.filename or "")

    if ext not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(
            f"Unsupported file type '{ext}'. Only {supported} files are accepted."
        )

    raw_bytes = await file.read()

    if not raw_bytes:
        raise ValueError("The uploaded file is empty.")

    if ext == ".pdf":
        text = extract_text_advanced(BytesIO(raw_bytes))
    else:
        # Guard: should never reach here given the extension check above.
        raise ValueError(f"No extractor configured for '{ext}'.")

    if len(text.strip()) < MIN_RESUME_TEXT_LENGTH:
        raise ValueError(
            "The uploaded file produced too little text. "
            "Make sure the PDF contains selectable text (not a scanned image)."
        )

    return text
