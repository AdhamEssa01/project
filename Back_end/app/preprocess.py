import re

def strip_html(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    return text

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = strip_html(text)
    text = text.lower()
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"[^0-9a-zA-Z\u0600-\u06FF\s\.,;:!?\-\/()]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
