# app/model.py
from typing import List, Optional, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import joblib
import os

class TfidfJobMatcher:
    def __init__(self, max_features: int = 5000, stop_words: Optional[str] = "english"):
        self.vectorizer = TfidfVectorizer(max_features=max_features, stop_words=stop_words)
        self.job_texts: List[str] = []
        self.job_meta: List[Dict] = []  # Example: [{"id": 1, "title": "...", "raw": "..."}]
        self.job_vectors = None
        self.fitted = False

    def fit(self, job_texts: List[str], job_meta: Optional[List[Dict]] = None, also_fit_on_resumes: bool = False, resumes: Optional[List[str]] = None):
        if job_meta is None:
            job_meta = [{} for _ in job_texts]
        self.job_texts = job_texts
        self.job_meta = job_meta

        corpus = list(job_texts)
        if also_fit_on_resumes and resumes:
            corpus = corpus + list(resumes)

        X = self.vectorizer.fit_transform(corpus)
        self.job_vectors = X[:len(job_texts)]
        self.fitted = True
        return self

    def recommend(self, resume_text: str, top_k: int = 5):
        if not self.fitted:
            raise RuntimeError("Model not fitted. Call fit(...) first.")
        r_vec = self.vectorizer.transform([resume_text])
        sims = cosine_similarity(r_vec, self.job_vectors)[0]
        idx_sorted = np.argsort(-sims)
        results = []
        for idx in idx_sorted[:top_k]:
            results.append({
                "score": float(sims[idx]),
                "title": self.job_meta[idx].get("title", f"Job {idx+1}"),
                "job_text": self.job_texts[idx],
                "meta": self.job_meta[idx]
            })

        return results

    def batch_recommend(self, resumes: List[str], top_k: int = 5):

        return [self.recommend(r, top_k=top_k) for r in resumes]

    def save(self, path: str):
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.vectorizer, os.path.join(path, "vectorizer.joblib"))
        joblib.dump(self.job_texts, os.path.join(path, "job_texts.joblib"))
        joblib.dump(self.job_meta, os.path.join(path, "job_meta.joblib"))
        joblib.dump(self.job_vectors, os.path.join(path, "job_vectors.joblib"))
        joblib.dump(self.fitted, os.path.join(path, "fitted.joblib"))

    def load(self, path: str):
        required_files = ["vectorizer.joblib", "job_texts.joblib", "job_meta.joblib", "job_vectors.joblib", "fitted.joblib"]
        for filename in required_files:
            filepath = os.path.join(path, filename)
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Model file not found: {filepath}. Please train the model first.")
        
        try:
            self.vectorizer = joblib.load(os.path.join(path, "vectorizer.joblib"))
            self.job_texts = joblib.load(os.path.join(path, "job_texts.joblib"))
            self.job_meta = joblib.load(os.path.join(path, "job_meta.joblib"))
            self.job_vectors = joblib.load(os.path.join(path, "job_vectors.joblib"))
            self.fitted = joblib.load(os.path.join(path, "fitted.joblib"))
        except Exception as e:
            raise RuntimeError(f"Error loading model files: {str(e)}")
        return self
