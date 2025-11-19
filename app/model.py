# app/model.py
from __future__ import annotations

import os
from typing import Dict, Optional, Tuple

import joblib

from app.preprocess import clean_text

MODEL_DIR = os.path.join(os.getcwd(), "saved_model")
PIPELINE_FILENAME = "job_match_pipeline.joblib"
CLASS_LABELS = ["No Fit", "Potential Fit", "Good Fit"]


class JobFitClassifier:
    """
    Helper wrapper around the persisted scikit-learn Pipeline that
    performs text pair classification (resume vs. job description).
    """

    def __init__(self, model_path: Optional[str] = None):
        default_path = os.path.join(MODEL_DIR, PIPELINE_FILENAME)
        self.model_path = model_path or default_path
        self.pipeline = None

    def load(self) -> "JobFitClassifier":
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Trained pipeline not found at {self.model_path}. "
                "Run scripts/train.py to create it."
            )
        self.pipeline = joblib.load(self.model_path)
        return self

    def _ensure_loaded(self):
        if self.pipeline is None:
            raise RuntimeError("Pipeline is not loaded. Call load() first.")

    def predict(
        self, resume_text: str, job_description_text: str
    ) -> Tuple[str, Dict[str, float]]:
        self._ensure_loaded()
        resume_clean = clean_text(resume_text)
        job_clean = clean_text(job_description_text)
        merged = f"{resume_clean} [SEP] {job_clean}".strip()

        probs = self.pipeline.predict_proba([merged])[0]
        predicted = self.pipeline.predict([merged])[0]
        probability_map = {label: 0.0 for label in CLASS_LABELS}
        for label, prob in zip(self.pipeline.classes_, probs):
            probability_map[label] = float(prob)

        return predicted, probability_map


def load_model(model_path: Optional[str] = None) -> JobFitClassifier:
    """
    Convenience function used by the API to load the persisted pipeline.
    """
    classifier = JobFitClassifier(model_path=model_path)
    classifier.load()
    return classifier
