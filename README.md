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

#### Prediction endpoints and examples

- **Form (PDF upload)**
  - **Routes (aliases):** `POST /predict_fit`, `POST /predict_job_fit`, `POST /predict`, `POST /job-fit`
  - **Content type:** `multipart/form-data`
  - **Fields:**
    - `resume_text_pdf`: PDF file upload containing the candidate resume (field name is required)
    - `job_description_text`: form field containing the job description text
  - **Example (curl):**

```bash
curl -X POST "http://localhost:8000/predict_fit" \
  -F "resume_text_pdf=@/path/to/resume.pdf" \
  -F "job_description_text=We are looking for a data scientist..."
```

- **JSON (raw text)**
  - **Route:** `POST /predict_json`
  - **Content type:** `application/json`
  - **Body:**
    - `resume_text`: raw resume/CV text (string, required for JSON endpoint)
    - `job_description_text`: job description text (string)
  - **Example (curl):**

```bash
curl -X POST "http://localhost:8000/predict_json" \
  -H "Content-Type: application/json" \
  -d '{"resume_text":"Experienced software engineer...","job_description_text":"Looking for a backend engineer..."}'
```

- **Response (both endpoints):** JSON with label and similarity score. Example:

```json
{
  "label": "Good Fit",
  "score": 0.82
}
```

Note: A `422 Unprocessable Entity` usually means the request did not include required form fields (for example the file field name must be `resume_text_pdf`). A `404 Not Found` means the client called a route that does not exist; the aliases above are provided for compatibility.

All predictions are made strictly using the classifier trained on
`data/train.csv`; there is no dependency on external scraping or job pools.
