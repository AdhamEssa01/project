# api/api.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.model import TfidfJobMatcher
from app.preprocess import clean_text
from typing import List
import uvicorn
import os
import joblib

from io import BytesIO
from pdfminer.high_level import extract_text

app = FastAPI(title="Job Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = os.path.join(os.getcwd(), "saved_model")
matcher = TfidfJobMatcher()
matcher.load(MODEL_DIR)

COMMON_SKILLS = [
    "python", "java", "c++", "sql", "excel", "pandas", "react", "angular",
    "node.js", "machine learning", "deep learning", "data analysis",
    "django", "flask", "html", "css", "javascript", "linux", "git", "aws"
]

def extract_text_from_pdf(file: UploadFile) -> str:
    contents = file.file.read()
    buffer = BytesIO(contents)
    text = extract_text(buffer)
    return text

def extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    found = [skill for skill in COMMON_SKILLS if skill in text_lower]
    return sorted(set(found))

@app.post("/upload_cv_pdf")
async def upload_cv_pdf(file: UploadFile = File(...), top_k: int = 5):
    text = extract_text_from_pdf(file)
    cleaned = clean_text(text)
    skills = extract_skills(cleaned)

    results = matcher.recommend(cleaned, top_k=top_k)

    return {
        "extracted_skills": skills,
        "top_matches": [
                {
                    "title": r["title"],
                    "score": round(r["score"], 3),
                    "job_text": r["job_text"],
                    "meta": r["meta"]
                } for r in results
            ]
    }

if __name__ == "__main__":
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)
