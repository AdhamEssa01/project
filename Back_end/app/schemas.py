"""
Pydantic request and response schemas for the Job Fit Classification API.
"""

from __future__ import annotations

from pydantic import BaseModel


# ── Existing single-candidate schemas ────────────────────────────────────────

class PredictRequest(BaseModel):
    """Raw-text prediction request body."""
    resume_text: str
    job_description_text: str


class SingleFitResponse(BaseModel):
    """Response for single-candidate endpoints (/job-fit, /predict_json)."""
    label: str
    score: float


# ── Batch screening schemas ───────────────────────────────────────────────────

class CandidateResult(BaseModel):
    """Result for one candidate in a batch screening run."""
    filename: str
    rank: int
    label: str          # Good Fit | Potential Fit | No Fit
    score: float
    status: str         # shortlisted | review | rejected


class FileError(BaseModel):
    """Extraction or prediction error for a single uploaded file."""
    filename: str
    error: str


class ScreeningSummary(BaseModel):
    """Aggregate statistics for a batch screening run."""
    total_candidates: int
    good_fit_count: int
    potential_fit_count: int
    no_fit_count: int
    good_fit_pct: float
    potential_fit_pct: float
    no_fit_pct: float
    top_candidates: list[str]   # filenames of top-3 by score


class ScreeningResponse(BaseModel):
    """Full response for POST /screen."""
    job_description_preview: str    # first 120 chars of JD for reference
    summary: ScreeningSummary
    candidates: list[CandidateResult]
    errors: list[FileError]
