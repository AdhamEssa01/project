# api/api.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.model import TfidfJobMatcher
from app.preprocess import clean_text
from app.pdf_utils import extract_text_advanced
from app.skill_extractor import extract_skills_spacy
from io import BytesIO
import uvicorn
import os

app = FastAPI(title="Job Recommendation API (Real Jobs)")

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
        print("✅ Model loaded successfully (Real Jobs).")
    except Exception as e:
        matcher = None
        print(f"❌ Error loading model: {str(e)}")
        print("⚠️ Run scripts/train.py first to create the model.")
else:
    print("⚠️ Model not found. Run scripts/train.py first.")


# Extract text from CV PDF
async def extract_text_from_pdf(file: UploadFile) -> str:
    contents = BytesIO(await file.read())
    return extract_text_advanced(contents)


# Main endpoint for uploading CV
@app.post("/upload_cv_pdf")
async def upload_cv_pdf(file: UploadFile = File(...), top_k: int = 5):
    """
    User uploads a CV in PDF format.
    The system extracts text and skills,
    then matches them with real jobs from the model.
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

    # Get job recommendations
    try:
        results = matcher.recommend(cleaned, top_k=top_k)
    except Exception as e:
        return {"error": f"Error generating recommendations: {str(e)}"}

    # Prepare response
    response = {
        "extracted_skills": skills,
        "matches_found": len(results),
        "top_matches": []
    }

    for r in results:
        meta = r.get("meta", {})
        response["top_matches"].append({
            "title": meta.get("title", "N/A"),
            "company": meta.get("company", "Unknown"),
            "category": meta.get("category", "Unspecified"),
            "location": meta.get("location", "Not provided"),
            "score": round(r.get("score", 0.0), 3),
            "apply_link": meta.get("url", "N/A"),
            "job_text": r.get("job_text", "")[:400]  # First 400 characters of description
        })

    return response


# Run the server locally
if __name__ == "__main__":
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)
