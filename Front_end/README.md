# Frontend

This package contains the recruiter-facing Angular application for the Job Fit Classifier workspace. It provides the landing page, the batch CV screening form, and the ranked results dashboard that consumes the FastAPI backend.

For the full project overview, see the [root README](../README.md).

## Product Flow

- Landing page introduces the screening workflow and routes the user into the app.
- Analyze page accepts one job description and multiple PDF resumes.
- Results page shows screening totals, ranked candidates, fit labels, and file-level warnings.

## Tech Stack

- Angular 21 with standalone components and router-based page flow
- PrimeNG 21 and PrimeIcons for buttons, toast feedback, table, tags, and progress bars
- Angular `HttpClient` for backend API calls

## API Integration

The frontend uses `src/environments/environment.ts` and currently points to:

```ts
apiBase: 'http://127.0.0.1:8000'
```

The main service is `src/app/services/job-fit.service.ts`:

- `screen(files, jobDescription)` -> `POST /screen`
- `analyze(file, jobDescription)` -> `POST /job-fit`

## PrimeNG Components In Use

- `p-button` for primary and secondary actions
- `p-toast` for validation and API error feedback
- `p-progressSpinner` while screening is in progress
- `p-table` for ranked candidate results
- `p-tag` for fit labels
- `p-progressBar` for candidate match scores
- `p-message` for warnings such as failed file processing

## Local Development

Install dependencies and run the Angular dev server:

```bash
npm install
npm start
```

Open `http://localhost:4200`.

## Build and Test

```bash
npm run build
npm test
```

## Relevant Files

- `src/app/features/landing/` - landing page
- `src/app/features/analyze/` - recruiter batch upload form
- `src/app/features/results/` - ranked screening results
- `src/app/services/job-fit.service.ts` - HTTP integration with the backend

