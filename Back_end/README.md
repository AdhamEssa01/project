# Backend

This package contains the FastAPI API, training scripts, and saved model assets for the Job Fit Classifier project. For the workspace-level overview and frontend links, see the [root README](../README.md).

## Project Overview

The backend serves recruiter-facing screening workflows on top of a scikit-learn TF-IDF + Logistic Regression model trained from `data/train.csv`.

- `POST /screen` is the primary batch screening endpoint used by the Angular app
- `POST /job-fit` handles single PDF resume scoring
- `POST /predict_json` handles raw text scoring for integrations or testing

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the classifier

```bash
python scripts/train.py
```

Training saves:

- `saved_model/job_match_pipeline.joblib`
- `saved_model/evaluation.json`

### 3. Run the API

```bash
uvicorn api.api:app --host 0.0.0.0 --port 8000 --reload
```

The API loads the trained pipeline on startup. If the model is missing, the service returns `503` until `scripts/train.py` has been run.

## Endpoints

### `POST /screen`

Batch CV screening for one job description and multiple resume PDFs.

- Content type: `multipart/form-data`
- Fields:
  - `resumes`: one or more PDF files
  - `job_description_text`: required text, minimum 30 characters
- Limits:
  - PDF only
  - Maximum 50 files per request

```bash
curl -X POST "http://localhost:8000/screen" \
  -F "resumes=@alice.pdf" \
  -F "resumes=@bob.pdf" \
  -F "job_description_text=We are looking for a senior data scientist..."
```

Returns ranked candidates, summary counts and percentages, and an `errors` array for files that could not be processed.

### `POST /job-fit`

Single resume PDF screening.

- Content type: `multipart/form-data`
- Fields:
  - `resume_text_pdf`: one PDF file
  - `job_description_text`: required text, minimum 30 characters
- Aliases kept for backward compatibility:
  - `/predict_fit`
  - `/predict_job_fit`
  - `/predict`

```bash
curl -X POST "http://localhost:8000/job-fit" \
  -F "resume_text_pdf=@resume.pdf" \
  -F "job_description_text=We are looking for a data scientist..."
```

### `POST /predict_json`

Single-candidate scoring using raw text instead of a PDF upload.

- Content type: `application/json`
- Body:
  - `resume_text`: required non-empty string
  - `job_description_text`: required text, minimum 30 characters

```bash
curl -X POST "http://localhost:8000/predict_json" \
  -H "Content-Type: application/json" \
  -d "{\"resume_text\":\"Experienced software engineer...\",\"job_description_text\":\"Looking for a backend engineer...\"}"
```

## Validation and Runtime Notes

- `422 Unprocessable Entity` is returned for invalid form fields or short job descriptions.
- `400 Bad Request` is returned for invalid PDFs or empty `resume_text`.
- `503 Service Unavailable` is returned when the model is not loaded.
- Files that fail extraction in `/screen` are reported individually without aborting the rest of the batch.
