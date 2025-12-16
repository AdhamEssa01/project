# app/model.py
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
VECTORIZER_FILENAME = "job_match_pipeline.joblib"  # Keep same filename for compatibility
THRESHOLDS_FILENAME = "thresholds.json"

# Default thresholds (fallback if thresholds.json not found)
DEFAULT_POTENTIAL_FIT_THRESHOLD = 0.40
DEFAULT_GOOD_FIT_THRESHOLD = 0.70


class JobFitClassifier:
    """
    Cosine similarity-based job-CV matching classifier.
    
    This class loads a pre-trained TF-IDF vectorizer (or extracts it from an
    old Pipeline artifact), computes cosine similarity between CV and job
    description texts, and classifies the match based on optimized thresholds
    loaded from saved_model/thresholds.json (or uses defaults if not found).
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        potential_fit_threshold: Optional[float] = None,
        good_fit_threshold: Optional[float] = None,
    ):
        default_path = os.path.join(MODEL_DIR, VECTORIZER_FILENAME)
        self.model_path = model_path or default_path
        self.vectorizer: Optional[TfidfVectorizer] = None
        
        # Thresholds can be set via constructor, loaded from file, or use defaults
        self.potential_fit_threshold = potential_fit_threshold
        self.good_fit_threshold = good_fit_threshold

    def _load_vectorizer(self):
        """
        Load the stored artifact. Backward-compatible:
        - If a Pipeline was previously saved (old LogisticRegression pipeline),
          extract the 'tfidf' step.
        - If a TfidfVectorizer was saved (new flow), use it directly.
        """
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
        """
        Load thresholds from JSON file, or use defaults if not found.
        
        Returns:
            Tuple of (potential_fit_threshold, good_fit_threshold)
        """
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
        
        # Use defaults if file doesn't exist or loading failed
        return DEFAULT_POTENTIAL_FIT_THRESHOLD, DEFAULT_GOOD_FIT_THRESHOLD

    def load(self) -> "JobFitClassifier":
        """
        Load the pre-trained TF-IDF vectorizer and thresholds from disk.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Trained vectorizer not found at {self.model_path}. "
                "Run scripts/train.py to create it."
            )
        self._load_vectorizer()
        
        # Load thresholds if not already set via constructor
        if self.potential_fit_threshold is None or self.good_fit_threshold is None:
            potential, good = self._load_thresholds()
            self.potential_fit_threshold = potential
            self.good_fit_threshold = good
        
        return self

    def _ensure_loaded(self):
        if self.vectorizer is None:
            raise RuntimeError("Vectorizer is not loaded. Call load() first.")

    def _classify_by_threshold(self, similarity_score: float) -> str:
        """
        Classify the match based on cosine similarity score using loaded thresholds.
        
        Thresholds:
        - score >= good_fit_threshold → "Good Fit"
        - potential_fit_threshold <= score < good_fit_threshold → "Potential Fit"
        - score < potential_fit_threshold → "No Fit"
        
        Args:
            similarity_score: Cosine similarity score between 0 and 1
        
        Returns:
            Classification label: "Good Fit", "Potential Fit", or "No Fit"
        """
        self._ensure_loaded()
        
        # Ensure thresholds are set
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
        
        # Step 4: Classify based on fixed thresholds
        classification = self._classify_by_threshold(similarity_score)
        
        return classification, similarity_score


def load_model(model_path: Optional[str] = None) -> JobFitClassifier:
    """
    Convenience function used by the API to load the persisted TF-IDF vectorizer
    and optimized thresholds.
    """
    classifier = JobFitClassifier(model_path=model_path)
    classifier.load()
    return classifier
