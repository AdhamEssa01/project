## Job Fit Classifier

This project trains and serves a supervised classifier that predicts whether a
candidate resume is a **No Fit**, **Potential Fit**, or **Good Fit** for a job
description. The model is trained **exclusively** on `data/train.csv`, which
contains paired resume and job description text plus the ground-truth label.

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the classifier

```bash
python scripts/train.py
```

The script performs the following steps:

- loads `data/train.csv`
- cleans and concatenates the resume & job description text fields
- normalizes labels into `No Fit`, `Potential Fit`, or `Good Fit`
- trains a TF-IDF + Logistic Regression model
- evaluates the model on a hold-out split
- saves the trained pipeline (`saved_model/job_match_pipeline.joblib`)
  and evaluation report (`saved_model/evaluation.json`)

### 3. Run the API

```bash
uvicorn api.api:app --host 0.0.0.0 --port 8000 --reload
```

The API automatically loads the saved pipeline on startup.

---

### Endpoints

#### `POST /screen` — Batch recruiter screening *(primary endpoint)*

Accepts one job description and **multiple PDF resumes** in a single request.
Returns ranked candidates, aggregate statistics, and any per-file extraction
errors (a bad file does not abort the rest of the batch).

- **Content type:** `multipart/form-data`
- **Fields:**
  - `resumes`: one or more PDF files (field name required; max 50 files)
  - `job_description_text`: the job requirement text (min 30 chars)

```bash
curl -X POST "http://localhost:8000/screen" \
  -F "resumes=@alice.pdf" \
  -F "resumes=@bob.pdf" \
  -F "job_description_text=We are looking for a senior data scientist..."
```

**Example response:**

```json
{
  "job_description_preview": "We are looking for a senior data scientist...",
  "summary": {
    "total_candidates": 2,
    "good_fit_count": 1,
    "potential_fit_count": 1,
    "no_fit_count": 0,
    "good_fit_pct": 50.0,
    "potential_fit_pct": 50.0,
    "no_fit_pct": 0.0,
    "top_candidates": ["alice.pdf", "bob.pdf"]
  },
  "candidates": [
    { "filename": "alice.pdf", "rank": 1, "label": "Good Fit",      "score": 0.83, "status": "shortlisted" },
    { "filename": "bob.pdf",   "rank": 2, "label": "Potential Fit", "score": 0.55, "status": "review"      }
  ],
  "errors": []
}
```

---

#### `POST /job-fit` — Single CV screening (PDF upload)

Aliases: `/predict_fit`, `/predict_job_fit`, `/predict`

- **Content type:** `multipart/form-data`
- **Fields:**
  - `resume_text_pdf`: one PDF file
  - `job_description_text`: job description text

```bash
curl -X POST "http://localhost:8000/job-fit" \
  -F "resume_text_pdf=@resume.pdf" \
  -F "job_description_text=We are looking for a data scientist..."
```

**Response:**

```json
{ "label": "Good Fit", "score": 0.82 }
```

---

#### `POST /predict_json` — Single CV screening (raw JSON text)

- **Content type:** `application/json`
- **Body:**
  - `resume_text`: raw resume text (string)
  - `job_description_text`: job description text (string)

```bash
curl -X POST "http://localhost:8000/predict_json" \
  -H "Content-Type: application/json" \
  -d '{"resume_text":"Experienced software engineer...","job_description_text":"Looking for a backend engineer..."}'
```

**Response:**

```json
{ "label": "Good Fit", "score": 0.82 }
```

---

### File upload rules

- **Accepted format:** PDF only (`.pdf`)
- **Maximum files per `/screen` request:** 50
- Files that fail to parse are reported in the `errors` array; the rest of the batch continues

### Notes

- A `422 Unprocessable Entity` means a required field is missing or fails validation.
- A `503 Service Unavailable` means the model has not been loaded yet; run `scripts/train.py`.
- All predictions are made strictly using the classifier trained on `data/train.csv`.
