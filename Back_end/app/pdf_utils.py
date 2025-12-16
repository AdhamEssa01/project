# app/pdf_utils.py
import pdfplumber
import re
from io import BytesIO

def extract_text_advanced(file_bytes: BytesIO) -> str:
    text_pages = []

    try:
        with pdfplumber.open(file_bytes) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                text_pages.append(text)
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")

    full_text = "\n".join(text_pages)

    cleaned = clean_pdf_text(full_text)
    return cleaned


def clean_pdf_text(text: str) -> str:
    text = re.sub(r"[•▪●■□◆►→⇨]", " ", text)
    text = re.sub(r"http\S+|Page\s*\d+\s*(of\s*\d+)?", " ", text)
    lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 2]
    merged = []
    for line in lines:
        if merged and not line.endswith(('.', ':')):
            merged[-1] += " " + line
        else:
            merged.append(line)
    text = " ".join(merged)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
