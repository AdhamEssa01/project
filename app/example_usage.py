# app/example_usage.py
from app.preprocess import clean_text
from app.model import TfidfJobMatcher

def demo():
    jobs = [
        "Python backend developer with experience in Django, REST APIs, and PostgreSQL.",
        "Frontend engineer skilled in React, TypeScript and CSS.",
        "Machine Learning engineer experienced in NLP, PyTorch and model deployment."
    ]
    meta = [
        {"id": 1, "title": "Backend Python Developer"},
        {"id": 2, "title": "Frontend React Engineer"},
        {"id": 3, "title": "ML/NLP Engineer"}
    ]

    resumes = [
        "I am a software engineer experienced in python, django, building REST services and using Postgres.",
        "Front-end developer. Strong skills in React, JavaScript, TypeScript and responsive CSS.",
        "Researcher with experience in natural language processing, pytorch and deploying models."
    ]

    jobs_clean = [clean_text(t) for t in jobs]
    resumes_clean = [clean_text(r) for r in resumes]

    matcher = TfidfJobMatcher(max_features=4000, stop_words='english')
    matcher.fit(job_texts=jobs_clean, job_meta=meta, also_fit_on_resumes=True, resumes=resumes_clean)

    for i, r in enumerate(resumes_clean):
        print(f"\n=== Resume {i+1} recommendations ===")
        recs = matcher.recommend(r, top_k=3)
        for rank, rec in enumerate(recs, start=1):
            print(f"{rank}. {rec['meta'].get('title','-')} (score={rec['score']:.3f})")

if __name__ == "__main__":
    demo()
