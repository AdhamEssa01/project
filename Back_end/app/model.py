from __future__ import annotations

import json
import os
from typing import Optional, Tuple

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import Pipeline

from app.preprocess import clean_text

MODEL_DIR = os.path.join(os.getcwd(), "saved_model")
VECTORIZER_FILENAME = "job_match_pipeline.joblib"
THRESHOLDS_FILENAME = "thresholds.json"

DEFAULT_POTENTIAL_FIT_THRESHOLD = 0.40
DEFAULT_GOOD_FIT_THRESHOLD = 0.70


class JobFitClassifier:

    def __init__(
        self,
        model_path: Optional[str] = None,
        potential_fit_threshold: Optional[float] = None,
        good_fit_threshold: Optional[float] = None,
    ):
        default_path = os.path.join(MODEL_DIR, VECTORIZER_FILENAME)
        self.model_path = model_path or default_path
        self.vectorizer: Optional[TfidfVectorizer] = None
        
        self.potential_fit_threshold = potential_fit_threshold
        self.good_fit_threshold = good_fit_threshold

    def _load_vectorizer(self):
        artifact = joblib.load(self.model_path)

        if isinstance(artifact, Pipeline):
            if "tfidf" not in artifact.named_steps:
                raise ValueError(
                    "Loaded pipeline does not contain a 'tfidf' step. "
                    "Please retrain with scripts/train.py."
                )
            self.vectorizer = artifact.named_steps["tfidf"]
            return

        if isinstance(artifact, TfidfVectorizer):
            self.vectorizer = artifact
            return

        raise TypeError(
            "Unsupported model artifact type. Expected Pipeline or TfidfVectorizer. "
            "Please retrain with scripts/train.py."
        )

    def _load_thresholds(self) -> Tuple[float, float]:
        thresholds_path = os.path.join(MODEL_DIR, THRESHOLDS_FILENAME)
        
        if os.path.exists(thresholds_path):
            try:
                with open(thresholds_path, "r", encoding="utf-8") as f:
                    thresholds_data = json.load(f)
                
                potential = thresholds_data.get("potential_fit_threshold", DEFAULT_POTENTIAL_FIT_THRESHOLD)
                good = thresholds_data.get("good_fit_threshold", DEFAULT_GOOD_FIT_THRESHOLD)
                
                return float(potential), float(good)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"[warn] Failed to load thresholds from {thresholds_path}: {e}")
                print(f"[warn] Using default thresholds")
        
        return DEFAULT_POTENTIAL_FIT_THRESHOLD, DEFAULT_GOOD_FIT_THRESHOLD

    def load(self) -> "JobFitClassifier":
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Trained vectorizer not found at {self.model_path}. "
                "Run scripts/train.py to create it."
            )
        self._load_vectorizer()
        
        if self.potential_fit_threshold is None or self.good_fit_threshold is None:
            potential, good = self._load_thresholds()
            self.potential_fit_threshold = potential
            self.good_fit_threshold = good
        
        return self

    def _ensure_loaded(self):
        if self.vectorizer is None:
            raise RuntimeError("Vectorizer is not loaded. Call load() first.")

    def _classify_by_threshold(self, similarity_score: float) -> str:
        self._ensure_loaded()
        
        if self.potential_fit_threshold is None or self.good_fit_threshold is None:
            potential, good = self._load_thresholds()
            self.potential_fit_threshold = potential
            self.good_fit_threshold = good

        if similarity_score >= self.good_fit_threshold:
            return "Good Fit"
        elif similarity_score >= self.potential_fit_threshold:
            return "Potential Fit"
        else:
            return "No Fit"

    def predict(
        self, resume_text: str, job_description_text: str
    ) -> Tuple[str, float]:
        self._ensure_loaded()
        
        resume_clean = clean_text(resume_text)
        job_clean = clean_text(job_description_text)
        
        resume_vector = self.vectorizer.transform([resume_clean])
        job_vector = self.vectorizer.transform([job_clean])
        
        similarity_matrix = cosine_similarity(resume_vector, job_vector)
        similarity_score = float(similarity_matrix[0][0])
        
        similarity_score = max(0.0, min(1.0, similarity_score))
        
        classification = self._classify_by_threshold(similarity_score)
        
        return classification, similarity_score


def load_model(model_path: Optional[str] = None) -> JobFitClassifier:
    classifier = JobFitClassifier(model_path=model_path)
    classifier.load()
    return classifier
