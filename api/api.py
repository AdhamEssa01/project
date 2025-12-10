# api/api.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from typing import Optional
import uvicorn

from app.model import JobFitClassifier, load_model
from app.pdf_utils import extract_text_advanced

app = FastAPI(title="Job Fit Classification API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier: Optional[JobFitClassifier] = None


def _load_classifier():
    global classifier
    try:
        classifier = load_model()
        print("Job Fit classifier loaded.")
    except Exception as exc:
        classifier = None
        print(f"Failed to load classifier: {exc}")
        print("Run scripts/train.py to generate saved_model/job_match_pipeline.joblib (TF-IDF vectorizer).")


@app.on_event("startup")
def startup_event():
    _load_classifier()


async def extract_text_from_pdf(file: UploadFile) -> str:
    contents = BytesIO(await file.read())
    return extract_text_advanced(contents)


@app.post("/job-fit")
async def predict_fit(
    resume_text_pdf: UploadFile = File(..., description="Resume PDF file"),
    job_description_text: str = Form(..., description="Job description text"),
):
    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run scripts/train.py first.",
        )

    try:
        resume_text = await extract_text_from_pdf(resume_text_pdf)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {exc}") from exc

    classification, similarity_score = classifier.predict(
        resume_text=resume_text,
        job_description_text=job_description_text,
    )

    return {
        "label": classification,
        "score": similarity_score,
    }


class PredictRequest(BaseModel):
    resume_text: Optional[str] = None
    job_description_text: str


@app.post("/predict_json")
async def predict_json(payload: PredictRequest):
    """Accept JSON payload with raw resume text and job description.

    Example JSON:
    {
      "resume_text": "...",
      "job_description_text": "..."
    }
    """
    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run scripts/train.py first.",
        )

    if not payload.resume_text:
        raise HTTPException(status_code=400, detail="`resume_text` is required in JSON payload")

    classification, similarity_score = classifier.predict(
        resume_text=payload.resume_text,
        job_description_text=payload.job_description_text,
    )

    return {"label": classification, "score": similarity_score}


if __name__ == "__main__":
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)
