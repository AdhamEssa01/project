# app/skill_extractor.py
import spacy
import re

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: spaCy model 'en_core_web_sm' not found. Please install it with: python -m spacy download en_core_web_sm")
    nlp = None

COMMON_SKILLS = [
    "python", "java", "c++", "c#", "sql", "html", "css", "javascript",
    "typescript", "react", "angular", "node.js", "django", "flask",
    "pandas", "numpy", "machine learning", "deep learning",
    "data analysis", "data visualization", "tensorflow", "pytorch",
    "linux", "git", "docker", "aws", "azure", "gcp", "kubernetes"
]

def extract_skills_spacy(text: str):
    if nlp is None:
        # Fallback to simple keyword matching if spaCy model is not loaded
        text_lower = text.lower()
        found_skills = set()
        for skill in COMMON_SKILLS:
            if re.search(rf"\b{re.escape(skill)}\b", text_lower):
                found_skills.add(skill)
        return sorted(found_skills)
    
    text_lower = text.lower()
    doc = nlp(text_lower)
    found_skills = set()

    for skill in COMMON_SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text_lower):
            found_skills.add(skill)

    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART"]:
            token = ent.text.lower().strip()
            if len(token.split()) <= 3 and len(token) > 2:
                found_skills.add(token)

    for chunk in doc.noun_chunks:
        token = chunk.text.lower().strip()
        if len(token.split()) <= 3 and any(k in token for k in ["data", "developer", "engineer", "analysis", "learning"]):
            found_skills.add(token)

    clean_skills = sorted(found_skills)
    return clean_skills
