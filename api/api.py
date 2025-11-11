# api/api.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.model import TfidfJobMatcher
from app.preprocess import clean_text
from app.skill_extractor import extract_skills_spacy
from typing import List
import uvicorn
import os
from io import BytesIO
from app.pdf_utils import extract_text_advanced

app = FastAPI(title="Job Recommendation API")

# Allow connections from any frontend (e.g., Angular or React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model
MODEL_DIR = os.path.join(os.getcwd(), "saved_model")
matcher = None

if os.path.exists(MODEL_DIR):
    try:
        matcher = TfidfJobMatcher()
        matcher.load(MODEL_DIR)
        print("Model loaded successfully.")
    except Exception as e:
        matcher = None
        print(f"Error loading model: {str(e)}")
        print("Run scripts/train.py first to create the model.")
else:
    print("Model not found. Run scripts/train.py first.")

# Basic list of common skills (can be expanded later)
COMMON_SKILLS = [
    "python", "java", "c++", "sql", "excel", "pandas", "react", "angular",
    "node.js", "machine learning", "deep learning", "data analysis",
    "django", "flask", "html", "css", "javascript", "linux", "git", "aws"
]

# -------------------------------------
# Helper Functions
# -------------------------------------

async def extract_text_from_pdf(file: UploadFile) -> str:
    contents = BytesIO(await file.read())
    return extract_text_advanced(contents)

def extract_skills(text: str) -> List[str]:
    """Extract skills from text (basic initial method)"""
    text_lower = text.lower()
    found = [skill for skill in COMMON_SKILLS if skill in text_lower]
    return sorted(set(found))

# -------------------------------------
# Main API Endpoint
# -------------------------------------

@app.post("/upload_cv_pdf")
async def upload_cv_pdf(file: UploadFile = File(...), top_k: int = 5):
    """
    User uploads a CV in PDF format.
    The system extracts the text and skills,
    then matches them with jobs from the model and returns the top results.
    """
    if matcher is None:
        return {"error": "Model not loaded. Run scripts/train.py first."}

    # Extract and clean text
    try:
        text = await extract_text_from_pdf(file)
        cleaned = clean_text(text)
        skills = extract_skills_spacy(cleaned)
    except Exception as e:
        return {"error": f"Error processing PDF: {str(e)}"}

    # Get the best job matches
    try:
        results = matcher.recommend(cleaned, top_k=top_k)
    except Exception as e:
        return {"error": f"Error generating recommendations: {str(e)}"}

    # Prepare the final response
    response = {
        "extracted_skills": skills,
        "matches_found": len(results),
        "top_matches": []
    }

    for r in results:
        job_info = {
            "title": r.get("title", "N/A"),
            "company": r["meta"].get("company", "Unknown"),
            "category": r["meta"].get("category", "Unspecified"),
            "location": r["meta"].get("location", "Not provided"),
            "score": round(r["score"], 3),
            "job_text": r["job_text"]
        }
        response["top_matches"].append(job_info)

    return response

# -------------------------------------
# Run the server
# -------------------------------------

if __name__ == "__main__":
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)
