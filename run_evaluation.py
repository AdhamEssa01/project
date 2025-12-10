# run_evaluation.py
"""
Script to run evaluation on the trained model.

This script demonstrates how to:
1. Load the trained model
2. Evaluate predictions on test data
3. Show how similarity scores are matched to labels using thresholds
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.model import load_model
from app.evaluation import compute_metrics, generate_classification_report, get_confusion_matrix, CLASS_LABELS
from app.preprocess import clean_text
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

DATA_PATH = os.path.join("data", "train.csv")
MODEL_DIR = "saved_model"
VECTORIZER_FILENAME = "job_match_pipeline.joblib"
THRESHOLDS_FILENAME = "thresholds.json"


def load_test_data():
    """Load and preprocess test data."""
    if not os.path.exists(DATA_PATH):
        print(f"[error] Training data not found at {DATA_PATH}")
        return None, None
    
    df = pd.read_csv(DATA_PATH)
    required_cols = {"resume_text", "job_description_text", "label"}
    if not required_cols.issubset(df.columns):
        print(f"[error] Missing required columns in {DATA_PATH}")
        return None, None
    
    # Clean texts
    df["resume_clean"] = df["resume_text"].fillna("").apply(clean_text)
    df["job_clean"] = df["job_description_text"].fillna("").apply(clean_text)
    
    # Filter out empty texts
    df = df[
        (df["resume_clean"].str.len() > 0) 
        & (df["job_clean"].str.len() > 0)
    ]
    
    # Use a subset for evaluation (last 20% as test set)
    from sklearn.model_selection import train_test_split
    _, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df.get("label", None))
    
    return test_df, df


def explain_score_matching():
    """
    Explain how similarity scores are matched to labels using thresholds.
    """
    print("\n" + "=" * 80)
    print("HOW SCORES ARE MATCHED TO LABELS")
    print("=" * 80)
    
    # Load thresholds
    thresholds_path = os.path.join(MODEL_DIR, THRESHOLDS_FILENAME)
    if os.path.exists(thresholds_path):
        import json
        with open(thresholds_path, "r") as f:
            thresholds_data = json.load(f)
        potential_threshold = thresholds_data.get("potential_fit_threshold", 0.40)
        good_threshold = thresholds_data.get("good_fit_threshold", 0.70)
    else:
        potential_threshold = 0.40
        good_threshold = 0.70
        print("[warn] thresholds.json not found, using default thresholds")
    
    print(f"\nThresholds:")
    print(f"  - Potential Fit Threshold: {potential_threshold:.4f}")
    print(f"  - Good Fit Threshold: {good_threshold:.4f}")
    
    print(f"\nClassification Rules:")
    print(f"  +-------------------------------------------------------------+")
    print(f"  | If similarity_score >= {good_threshold:.4f}        -> 'Good Fit'      |")
    print(f"  | If {potential_threshold:.4f} <= similarity_score < {good_threshold:.4f} -> 'Potential Fit' |")
    print(f"  | If similarity_score < {potential_threshold:.4f}         -> 'No Fit'        |")
    print(f"  +-------------------------------------------------------------+")
    
    print(f"\nHow it works:")
    print(f"  1. The model computes cosine similarity between CV and job description")
    print(f"     - Similarity ranges from 0.0 (completely different) to 1.0 (identical)")
    print(f"  2. The similarity score is compared against two thresholds:")
    print(f"     - If score >= {good_threshold:.4f}: Strong match → 'Good Fit'")
    print(f"     - If score >= {potential_threshold:.4f} but < {good_threshold:.4f}: Moderate match → 'Potential Fit'")
    print(f"     - If score < {potential_threshold:.4f}: Weak match → 'No Fit'")
    print(f"  3. These thresholds are optimized during training using grid search")
    print(f"     to maximize the weighted F1-score on the validation set")
    
    print(f"\nExample scores and their classifications:")
    examples = [
        (0.85, "High similarity - strong match"),
        (0.75, "Above good threshold"),
        (0.65, "Between thresholds"),
        (0.50, "Above potential threshold"),
        (0.30, "Below potential threshold"),
        (0.10, "Very low similarity")
    ]
    
    for score, description in examples:
        if score >= good_threshold:
            label = "Good Fit"
        elif score >= potential_threshold:
            label = "Potential Fit"
        else:
            label = "No Fit"
        print(f"  Score: {score:.2f} → {label:15s} ({description})")


def main():
    print("Running Evaluation on Job-CV Matching Model")
    print("=" * 80)
    
    # Explain score matching first
    explain_score_matching()
    
    # Load model
    print("\n" + "=" * 80)
    print("LOADING MODEL")
    print("=" * 80)
    try:
        classifier = load_model()
        print("[info] Model loaded successfully")
    except FileNotFoundError as e:
        print(f"[error] {e}")
        print("[error] Please run scripts/train.py first to train the model")
        return
    
    # Load test data
    print("\n" + "=" * 80)
    print("LOADING TEST DATA")
    print("=" * 80)
    test_df, _ = load_test_data()
    if test_df is None:
        return
    
    print(f"[info] Loaded {len(test_df)} test examples")
    
    # Make predictions
    print("\n" + "=" * 80)
    print("MAKING PREDICTIONS")
    print("=" * 80)
    predictions = []
    scores = []
    true_labels = []
    
    for idx, row in test_df.iterrows():
        classification, similarity_score = classifier.predict(
            row["resume_clean"],
            row["job_clean"]
        )
        predictions.append(classification)
        scores.append(similarity_score)
        if "label" in row and pd.notna(row["label"]):
            true_labels.append(str(row["label"]).strip())
        else:
            true_labels.append(None)
    
    print(f"[info] Made {len(predictions)} predictions")
    print(f"\nSample predictions:")
    for i in range(min(5, len(predictions))):
        print(f"  Example {i+1}: Score={scores[i]:.4f} → {predictions[i]}")
        if true_labels[i]:
            print(f"            True Label: {true_labels[i]}")
    
    # Evaluate if we have true labels
    if any(true_labels) and all(l is not None for l in true_labels):
        print("\n" + "=" * 80)
        print("EVALUATION METRICS")
        print("=" * 80)
        
        # Normalize labels to match CLASS_LABELS
        label_map = {
            "no fit": "No Fit",
            "nofit": "No Fit",
            "not fit": "No Fit",
            "potential fit": "Potential Fit",
            "maybe fit": "Potential Fit",
            "good fit": "Good Fit",
            "strong fit": "Good Fit",
        }
        
        normalized_labels = []
        for label in true_labels:
            normalized = label_map.get(label.lower(), label)
            if normalized not in CLASS_LABELS:
                normalized = "No Fit"  # Default fallback
            normalized_labels.append(normalized)
        
        y_true = np.array(normalized_labels)
        y_pred = np.array(predictions)
        
        # Compute metrics
        metrics = compute_metrics(y_true, y_pred)
        
        print(f"\nOverall Accuracy: {metrics['accuracy']:.4f}")
        print(f"\nPer-Class Metrics:")
        for label in CLASS_LABELS:
            if label in metrics['per_class']:
                m = metrics['per_class'][label]
                print(f"  {label}:")
                print(f"    Precision: {m['precision']:.4f}")
                print(f"    Recall:    {m['recall']:.4f}")
                print(f"    F1-Score:  {m['f1_score']:.4f}")
                print(f"    Support:   {m['support']}")
        
        print(f"\nMacro Averages:")
        print(f"  Precision: {metrics['macro_avg']['precision']:.4f}")
        print(f"  Recall:    {metrics['macro_avg']['recall']:.4f}")
        print(f"  F1-Score:  {metrics['macro_avg']['f1_score']:.4f}")
        
        print(f"\nWeighted Averages:")
        print(f"  Precision: {metrics['weighted_avg']['precision']:.4f}")
        print(f"  Recall:    {metrics['weighted_avg']['recall']:.4f}")
        print(f"  F1-Score:  {metrics['weighted_avg']['f1_score']:.4f}")
        
        # Confusion matrix
        cm = get_confusion_matrix(y_true, y_pred)
        print(f"\nConfusion Matrix:")
        print(f"                Predicted")
        print(f"              ", "  ".join(f"{label:15s}" for label in CLASS_LABELS))
        for i, label in enumerate(CLASS_LABELS):
            print(f"{label:15s}", "  ".join(f"{cm[i][j]:15d}" for j in range(len(CLASS_LABELS))))
    else:
        print("\n[info] No true labels available for evaluation")
        print("[info] Showing score distribution instead:")
        print(f"  Mean score: {np.mean(scores):.4f}")
        print(f"  Std score:  {np.std(scores):.4f}")
        print(f"  Min score:  {np.min(scores):.4f}")
        print(f"  Max score:  {np.max(scores):.4f}")
    
    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

