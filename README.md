# Job Fit Classifier

Job Fit Classifier is a full-stack screening application for recruiters. The frontend provides a simple workflow for uploading multiple resume PDFs and a job description, while the backend extracts text, scores each candidate with a trained classifier, and returns ranked results.

## Architecture

- Frontend: Angular 21 standalone app with PrimeNG UI components
- Backend: FastAPI service for single-candidate and batch screening
- Model: scikit-learn TF-IDF + Logistic Regression pipeline trained on `Back_end/data/train.csv`

## Repository Layout

```text
.
|-- Front_end/   Angular recruiter UI
|-- Back_end/    FastAPI API, training scripts, model assets, and data
`-- README.md    Workspace overview and quick start
```

## Quick Start

### 1. Start the backend

```bash
cd Back_end
pip install -r requirements.txt
python scripts/train.py
uvicorn api.api:app --host 0.0.0.0 --port 8000 --reload
```

The API starts at `http://127.0.0.1:8000` and exposes the recruiter batch endpoint at `POST /screen`.

### 2. Start the frontend

```bash
cd Front_end
npm install
npm start
```

The Angular app starts at `http://localhost:4200` and targets the backend at `http://127.0.0.1:8000`.

## Package Docs

- Frontend details: [Front_end/README.md](Front_end/README.md)
- Backend details: [Back_end/README.md](Back_end/README.md)

## Core Workflow

1. Recruiter opens the landing page and moves to the screening form.
2. The frontend submits one job description plus up to 50 PDF resumes to `POST /screen`.
3. FastAPI extracts PDF text, runs the classifier, and returns ranked candidates, summary metrics, and per-file errors.
4. The frontend renders shortlist counts, fit labels, scores, and the ranked table on the results page.

