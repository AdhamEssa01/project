from __future__ import annotations

from io import BytesIO
from typing import Optional

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import MAX_FILES, MIN_JOB_DESCRIPTION_LENGTH
from app.file_utils import extract_text_from_upload
from app.model import JobFitClassifier, load_model
from app.schemas import PredictRequest, ScreeningResponse, SingleFitResponse
from app.screening_service import screen_candidates

app = FastAPI(
    title="Job Fit Classification API",
    description=(
        "Recruiter-facing batch CV screening and single-candidate job-fit inference. "
        "Accepts PDF resumes only."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier: Optional[JobFitClassifier] = None


# ── Startup ───────────────────────────────────────────────────────────────────

def _load_classifier() -> None:
    global classifier
    try:
        classifier = load_model()
        print("Job Fit classifier loaded.")
    except Exception as exc:
        classifier = None
        print(f"Failed to load classifier: {exc}")
        print("Run scripts/train.py to generate saved_model/job_match_pipeline.joblib.")


@app.on_event("startup")
def startup_event() -> None:
    _load_classifier()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _require_classifier() -> JobFitClassifier:
    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run scripts/train.py first.",
        )
    return classifier


def _validate_job_description(text: str) -> str:
    stripped = text.strip()
    if len(stripped) < MIN_JOB_DESCRIPTION_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=(
                f"job_description_text is too short "
                f"(minimum {MIN_JOB_DESCRIPTION_LENGTH} characters)."
            ),
        )
    return stripped


# ── Single-candidate endpoints (backward-compatible) ─────────────────────────

_SINGLE_FILE_ROUTES = ["/job-fit", "/predict_fit", "/predict_job_fit", "/predict"]


@app.post(
    _SINGLE_FILE_ROUTES[0],
    response_model=SingleFitResponse,
    summary="Single CV screening (PDF upload)",
    tags=["Single candidate"],
)
@app.post(_SINGLE_FILE_ROUTES[1], response_model=SingleFitResponse, include_in_schema=False)
@app.post(_SINGLE_FILE_ROUTES[2], response_model=SingleFitResponse, include_in_schema=False)
@app.post(_SINGLE_FILE_ROUTES[3], response_model=SingleFitResponse, include_in_schema=False)
async def predict_fit(
    resume_text_pdf: UploadFile = File(..., description="Resume PDF file"),
    job_description_text: str = Form(..., description="Job description text"),
) -> SingleFitResponse:
    """Screen a single candidate CV (PDF) against a job description."""
    clf = _require_classifier()
    jd = _validate_job_description(job_description_text)

    try:
        resume_text = await extract_text_from_upload(resume_text_pdf)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    label, score = clf.predict(resume_text=resume_text, job_description_text=jd)
    return SingleFitResponse(label=label, score=round(score, 4))


@app.post(
    "/predict_json",
    response_model=SingleFitResponse,
    summary="Single CV screening (raw JSON text)",
    tags=["Single candidate"],
)
async def predict_json(payload: PredictRequest) -> SingleFitResponse:
    """Screen a single candidate using raw resume and job description text."""
    clf = _require_classifier()
    jd = _validate_job_description(payload.job_description_text)

    resume = payload.resume_text.strip()
    if not resume:
        raise HTTPException(status_code=400, detail="`resume_text` must not be empty.")

    label, score = clf.predict(resume_text=resume, job_description_text=jd)
    return SingleFitResponse(label=label, score=round(score, 4))


# ── Batch screening endpoint ──────────────────────────────────────────────────

@app.post(
    "/screen",
    response_model=ScreeningResponse,
    summary="Batch CV screening (multiple PDFs against one job description)",
    tags=["Batch screening"],
)
async def screen(
    resumes: list[UploadFile] = File(..., description="One or more PDF resume files"),
    job_description_text: str = Form(..., description="Job description text"),
) -> ScreeningResponse:
    """
    Screen multiple candidates against a single job description in one request.

    Returns ranked candidates, per-file errors, and aggregate summary statistics.
    Files that fail extraction are reported individually without aborting the batch.
    """
    clf = _require_classifier()
    jd = _validate_job_description(job_description_text)

    if len(resumes) > MAX_FILES:
        raise HTTPException(
            status_code=422,
            detail=f"Too many files. Maximum allowed per request is {MAX_FILES}.",
        )

    return await screen_candidates(files=resumes, job_description_text=jd, classifier=clf)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("api.api:app", host="0.0.0.0", port=8000, reload=True)
