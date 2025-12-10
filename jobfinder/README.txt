Job Finder – Simple Front-End (HTML / CSS / JS)
=================================================

Structure:
- index.html     -> Landing page (Get Start)
- analyze.html   -> Upload CV + Job Description + result
- styles.css     -> UI styles (responsive)
- script.js      -> Navigation + API call + result handling

How to run:
1. Open the folder in VS Code.
2. Use the "Live Server" extension OR open index.html directly in the browser.
3. Click "Get Start" to go to analyze.html.
4. Upload CV (PDF/DOC/DOCX) and paste the job description.
5. Click "Analyze Fit".

API config:
- Open script.js and check the CONFIG section at the top.
- Make sure:
  - API_BASE_URL is correct.
  - API_ENDPOINT matches the path in /docs (e.g. /predict_job_fit or similar).
  - Field names 'cv_file' and 'job_description' match the API docs.

If you just want to test the UI without the backend:
- In script.js set: const USE_MOCK_API = true;
- The app will show a random result (Fit / Not Fit / Good Fit) without calling the API.
