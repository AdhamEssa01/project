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

#### Prediction endpoint

- **Route:** `POST /predict_fit`
- **Request body:**
  - `resume_text_pdf`: PDF file upload containing the candidate resume.
  - `job_description_text`: Form field containing the job description text.
- **Response:**
  ```json
  {
    "predicted_fit": "Good Fit",
    "class_probabilities": {
      "No Fit": 0.02,
      "Potential Fit": 0.18,
      "Good Fit": 0.80
    }
  }
  ```

All predictions are made strictly using the classifier trained on
`data/train.csv`; there is no dependency on external scraping or job pools.
