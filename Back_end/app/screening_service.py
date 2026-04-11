"""
Batch screening service.

Orchestrates multi-file CV extraction, scoring, ranking, and summary
statistics for the recruiter-facing POST /screen endpoint.
"""

from __future__ import annotations

from fastapi import UploadFile

from app.file_utils import extract_text_from_upload
from app.model import JobFitClassifier
from app.schemas import (
    CandidateResult,
    FileError,
    ScreeningResponse,
    ScreeningSummary,
)

# Label → recruiter-facing status mapping
_STATUS_MAP: dict[str, str] = {
    "Good Fit": "shortlisted",
    "Potential Fit": "review",
    "No Fit": "rejected",
}


def _safe_pct(count: int, total: int) -> float:
    """Return percentage rounded to 1 decimal place; 0 if total is 0."""
    if total == 0:
        return 0.0
    return round(count / total * 100, 1)


async def screen_candidates(
    files: list[UploadFile],
    job_description_text: str,
    classifier: JobFitClassifier,
) -> ScreeningResponse:
    """
    Screen a list of uploaded CV files against a single job description.

    Per-file extraction or prediction failures are isolated and returned
    in the `errors` list without aborting the entire batch.

    Args:
        files: List of uploaded PDF files.
        job_description_text: Raw job requirement text.
        classifier: Loaded JobFitClassifier instance.

    Returns:
        A fully populated ScreeningResponse with ranked candidates,
        aggregate statistics, and per-file errors.
    """
    successful: list[CandidateResult] = []
    errors: list[FileError] = []

    for file in files:
        filename = file.filename or "unknown"
        try:
            resume_text = await extract_text_from_upload(file)
            label, score = classifier.predict(
                resume_text=resume_text,
                job_description_text=job_description_text,
            )
            successful.append(
                CandidateResult(
                    filename=filename,
                    rank=0,          # assigned after sorting
                    label=label,
                    score=round(score, 4),
                    status=_STATUS_MAP.get(label, "review"),
                )
            )
        except Exception as exc:
            errors.append(FileError(filename=filename, error=str(exc)))

    # Sort by score descending and assign ranks
    successful.sort(key=lambda c: c.score, reverse=True)
    for i, candidate in enumerate(successful, start=1):
        candidate.rank = i

    # Aggregate statistics
    total = len(successful)
    good_count = sum(1 for c in successful if c.label == "Good Fit")
    potential_count = sum(1 for c in successful if c.label == "Potential Fit")
    no_fit_count = sum(1 for c in successful if c.label == "No Fit")

    top_candidates = [c.filename for c in successful[:3]]

    summary = ScreeningSummary(
        total_candidates=total,
        good_fit_count=good_count,
        potential_fit_count=potential_count,
        no_fit_count=no_fit_count,
        good_fit_pct=_safe_pct(good_count, total),
        potential_fit_pct=_safe_pct(potential_count, total),
        no_fit_pct=_safe_pct(no_fit_count, total),
        top_candidates=top_candidates,
    )

    return ScreeningResponse(
        job_description_preview=job_description_text[:120].strip(),
        summary=summary,
        candidates=successful,
        errors=errors,
    )
