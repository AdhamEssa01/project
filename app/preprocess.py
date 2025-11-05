# app/preprocess.py
import re

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"[^0-9a-zA-Z\u0600-\u06FF\s\.,;:!?\-\/()]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
