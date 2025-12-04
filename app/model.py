# app/model.py
from __future__ import annotations

import os
from typing import Optional, Tuple

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.preprocess import clean_text

MODEL_DIR = os.path.join(os.getcwd(), "saved_model")
VECTORIZER_FILENAME = "job_match_pipeline.joblib"  # Keep same filename for compatibility


class JobFitClassifier:
    """
    Cosine similarity-based job-CV matching classifier.
    
    This class loads a pre-trained TF-IDF vectorizer and uses it to compute
    cosine similarity between CV and job description texts, then classifies
    the match based on fixed thresholds.
    """

    def __init__(self, model_path: Optional[str] = None):
        default_path = os.path.join(MODEL_DIR, VECTORIZER_FILENAME)
        self.model_path = model_path or default_path
        self.vectorizer: Optional[TfidfVectorizer] = None

    def load(self) -> "JobFitClassifier":
        """
        Load the pre-trained TF-IDF vectorizer from disk.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Trained vectorizer not found at {self.model_path}. "
                "Run scripts/train.py to create it."
            )
        self.vectorizer = joblib.load(self.model_path)
        return self

    def _ensure_loaded(self):
        if self.vectorizer is None:
            raise RuntimeError("Vectorizer is not loaded. Call load() first.")

    def _classify_by_threshold(self, similarity_score: float) -> str:
        """
        Classify the match based on cosine similarity score using fixed thresholds.
        
        Thresholds:
        - score >= 0.70 → "Good Fit"
        - 0.40 <= score < 0.70 → "Potential Fit"
        - score < 0.40 → "No Fit"
        
        Args:
            similarity_score: Cosine similarity score between 0 and 1
        
        Returns:
            Classification label: "Good Fit", "Potential Fit", or "No Fit"
        """
        if similarity_score >= 0.70:
            return "Good Fit"
        elif similarity_score >= 0.40:
            return "Potential Fit"
        else:
            return "No Fit"

    def predict(
        self, resume_text: str, job_description_text: str
    ) -> Tuple[str, float]:
        """
        Predict job-CV fit using cosine similarity.
        
        Process:
        1. Preprocess both texts separately
        2. Vectorize both texts using the loaded TF-IDF vectorizer
        3. Compute cosine similarity between the two vectors
        4. Classify based on fixed thresholds
        
        Args:
            resume_text: Raw CV/resume text
            job_description_text: Raw job description text
        
        Returns:
            Tuple of (classification, similarity_score)
            - classification: "Good Fit", "Potential Fit", or "No Fit"
            - similarity_score: Cosine similarity score between 0 and 1
        """
        self._ensure_loaded()
        
        # Step 1: Preprocess both texts separately
        resume_clean = clean_text(resume_text)
        job_clean = clean_text(job_description_text)
        
        # Step 2: Vectorize both texts separately using the TF-IDF vectorizer
        # This creates sparse vectors in the same feature space learned during training
        resume_vector = self.vectorizer.transform([resume_clean])
        job_vector = self.vectorizer.transform([job_clean])
        
        # Debugging info: vector shapes
        # Both vectors have shape (1, n_features) where n_features is the vocabulary size
        # (typically up to 20,000 features based on max_features in vectorizer)
        
        # Step 3: Compute cosine similarity
        # Cosine similarity formula: cos(θ) = (A · B) / (||A|| × ||B||)
        # where:
        #   - A · B = dot product of vectors A and B (sum of element-wise products)
        #   - ||A|| = L2 norm (magnitude) of vector A = sqrt(sum of squares)
        #   - ||B|| = L2 norm (magnitude) of vector B = sqrt(sum of squares)
        # 
        # For TF-IDF vectors (which are non-negative), cosine similarity ranges from 0 to 1:
        #   - 0 = completely different (orthogonal vectors, no shared terms)
        #   - 1 = identical (same term weights)
        # 
        # The sklearn cosine_similarity function computes this as:
        #   numerator = dot product (A · B)
        #   denominator = ||A|| × ||B||
        #   similarity = numerator / denominator
        similarity_matrix = cosine_similarity(resume_vector, job_vector)
        similarity_score = float(similarity_matrix[0][0])
        
        # Ensure score is in valid range [0, 1] (should always be for TF-IDF)
        similarity_score = max(0.0, min(1.0, similarity_score))
        
        # Step 4: Classify based on thresholds
        classification = self._classify_by_threshold(similarity_score)
        
        # Debugging info: which threshold was triggered
        # This is implicitly determined by the _classify_by_threshold method
        # but we can log it if needed for debugging
        
        return classification, similarity_score


def load_model(model_path: Optional[str] = None) -> JobFitClassifier:
    """
    Convenience function used by the API to load the persisted TF-IDF vectorizer.
    """
    classifier = JobFitClassifier(model_path=model_path)
    classifier.load()
    return classifier
