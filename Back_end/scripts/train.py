import json
import os
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split

from app.preprocess import clean_text

DATA_PATH = os.path.join("data", "train.csv")
MODEL_DIR = "saved_model"
VECTORIZER_FILENAME = "job_match_pipeline.joblib"
THRESHOLDS_FILENAME = "thresholds.json"
CLASS_LABELS = ["No Fit", "Potential Fit", "Good Fit"]

LABEL_NORMALIZATION = {
    "no fit": "No Fit",
    "nofit": "No Fit",
    "not fit": "No Fit",
    "poor fit": "No Fit",
    "bad fit": "No Fit",
    "0": "No Fit",
    "potential fit": "Potential Fit",
    "maybe fit": "Potential Fit",
    "possible fit": "Potential Fit",
    "moderate fit": "Potential Fit",
    "1": "Potential Fit",
    "good fit": "Good Fit",
    "strong fit": "Good Fit",
    "great fit": "Good Fit",
    "2": "Good Fit",
}


def normalize_label(raw: Optional[str]) -> Optional[str]:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    text = str(raw).strip()
    key = text.lower()
    return LABEL_NORMALIZATION.get(key, None)


def load_and_preprocess_dataset(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Training data not found at {path}")

    df = pd.read_csv(path)
    required_cols = {"resume_text", "job_description_text", "label"}
    if not required_cols.issubset(df.columns):
        missing = ", ".join(sorted(required_cols - set(df.columns)))
        raise ValueError(f"train.csv missing required columns: {missing}")

    df["resume_clean"] = df["resume_text"].fillna("").apply(clean_text)
    df["job_clean"] = df["job_description_text"].fillna("").apply(clean_text)
    
    df["label_normalized"] = df["label"].apply(normalize_label)
    
    df = df[
        (df["resume_clean"].str.len() > 0) 
        & (df["job_clean"].str.len() > 0)
        & (df["label_normalized"].notna())
    ]
    
    if df.empty:
        raise ValueError("No usable rows after cleaning and label normalization.")

    return df[["resume_clean", "job_clean", "label_normalized"]].rename(
        columns={"label_normalized": "label"}
    )


def build_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2),
        stop_words="english",
    )


def create_combined_corpus(df: pd.DataFrame) -> list:
    resume_texts = df["resume_clean"].tolist()
    job_texts = df["job_clean"].tolist()
    combined_corpus = resume_texts + job_texts
    return combined_corpus


def save_vectorizer(vectorizer: TfidfVectorizer) -> None:
    os.makedirs(MODEL_DIR, exist_ok=True)
    vectorizer_path = os.path.join(MODEL_DIR, VECTORIZER_FILENAME)
    dump(vectorizer, vectorizer_path)
    print(f"[info] Saved trained TF-IDF vectorizer to {vectorizer_path}")
    print(f"[info] Vocabulary size: {len(vectorizer.vocabulary_)} features")


def split_data(df: pd.DataFrame, test_size: float = 0.2, val_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_val_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=df["label"]
    )
    
    val_prop = val_size / (1 - test_size)
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=val_prop,
        random_state=random_state,
        stratify=train_val_df["label"]
    )
    
    return train_df, val_df, test_df


def compute_similarity_scores(
    df: pd.DataFrame, vectorizer: TfidfVectorizer
) -> np.ndarray:
    scores = []
    
    for _, row in df.iterrows():
        resume_vec = vectorizer.transform([row["resume_clean"]])
        job_vec = vectorizer.transform([row["job_clean"]])
        similarity = cosine_similarity(resume_vec, job_vec)[0][0]
        scores.append(float(similarity))
    
    return np.array(scores)

def classify_by_threshold(
    similarity_scores: np.ndarray, 
    potential_threshold: float, 
    good_threshold: float
) -> np.ndarray:
    predictions = []
    for score in similarity_scores:
        if score >= good_threshold:
            predictions.append("Good Fit")
        elif score >= potential_threshold:
            predictions.append("Potential Fit")
        else:
            predictions.append("No Fit")
    return np.array(predictions)


def find_optimal_thresholds(
    similarity_scores: np.ndarray,
    true_labels: np.ndarray,
    potential_range: Tuple[float, float] = (0.20, 0.60),
    good_range: Tuple[float, float] = (0.50, 0.90),
    step: float = 0.01
) -> Tuple[float, float, float]:
    from sklearn.metrics import f1_score
    
    best_f1 = 0.0
    best_potential = 0.40
    best_good = 0.70
    
    potential_values = np.arange(potential_range[0], potential_range[1] + step, step)
    good_values = np.arange(good_range[0], good_range[1] + step, step)
    
    print(f"[info] Grid searching over {len(potential_values) * len(good_values)} threshold combinations...")
    
    for potential_threshold in potential_values:
        for good_threshold in good_values:
            if good_threshold <= potential_threshold:
                continue
            
            predictions = classify_by_threshold(similarity_scores, potential_threshold, good_threshold)
            f1 = f1_score(true_labels, predictions, labels=CLASS_LABELS, average='weighted', zero_division=0)
            
            if f1 > best_f1:
                best_f1 = f1
                best_potential = potential_threshold
                best_good = good_threshold
    
    return best_potential, best_good, best_f1


def evaluate_thresholds(
    similarity_scores: np.ndarray,
    true_labels: np.ndarray,
    potential_threshold: float,
    good_threshold: float
) -> dict:
    from sklearn.metrics import (
        accuracy_score,
        precision_recall_fscore_support,
        classification_report,
        confusion_matrix
    )
    
    predictions = classify_by_threshold(similarity_scores, potential_threshold, good_threshold)
    
    accuracy = accuracy_score(true_labels, predictions)
    precision, recall, f1, support = precision_recall_fscore_support(
        true_labels, predictions, labels=CLASS_LABELS, zero_division=0
    )
    
    per_class_metrics = {}
    for i, label in enumerate(CLASS_LABELS):
        per_class_metrics[label] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1_score": float(f1[i]),
            "support": int(support[i])
        }
    
    macro_precision = float(np.mean(precision))
    macro_recall = float(np.mean(recall))
    macro_f1 = float(np.mean(f1))
    
    weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
        true_labels, predictions, labels=CLASS_LABELS, average='weighted', zero_division=0
    )
    
    cm = confusion_matrix(true_labels, predictions, labels=CLASS_LABELS)
    
    return {
        "accuracy": float(accuracy),
        "per_class": per_class_metrics,
        "macro_avg": {
            "precision": macro_precision,
            "recall": macro_recall,
            "f1_score": macro_f1
        },
        "weighted_avg": {
            "precision": float(weighted_precision),
            "recall": float(weighted_recall),
            "f1_score": float(weighted_f1)
        },
        "confusion_matrix": cm.tolist(),
        "classification_report": classification_report(
            true_labels, predictions, labels=CLASS_LABELS, output_dict=True, zero_division=0
        )
    }


def save_thresholds(
    potential_threshold: float,
    good_threshold: float,
    validation_f1: float,
    test_metrics: dict
) -> None:
    os.makedirs(MODEL_DIR, exist_ok=True)
    thresholds_path = os.path.join(MODEL_DIR, THRESHOLDS_FILENAME)
    
    thresholds_data = {
        "potential_fit_threshold": float(potential_threshold),
        "good_fit_threshold": float(good_threshold),
        "optimization_metrics": {
            "validation_f1": float(validation_f1),
            "test_accuracy": test_metrics["accuracy"],
            "test_weighted_f1": test_metrics["weighted_avg"]["f1_score"]
        },
        "test_metrics": test_metrics
    }
    
    with open(thresholds_path, "w", encoding="utf-8") as f:
        json.dump(thresholds_data, f, indent=2)
    
    print(f"[info] Saved optimized thresholds to {thresholds_path}")
    print(f"[info]   Potential Fit Threshold: {potential_threshold:.4f}")
    print(f"[info]   Good Fit Threshold: {good_threshold:.4f}")


def main():
    print("Training TF-IDF vectorizer for cosine similarity matching")
    print("=" * 60)
    
    df = load_and_preprocess_dataset(DATA_PATH)
    print(f"[info] Loaded {len(df)} training examples")
    
    train_df, val_df, test_df = split_data(df, test_size=0.2, val_size=0.2, random_state=42)
    print(f"[info] Data split:")
    print(f"[info]   Train: {len(train_df)} examples")
    print(f"[info]   Validation: {len(val_df)} examples")
    print(f"[info]   Test: {len(test_df)} examples")
    
    combined_corpus = create_combined_corpus(df)
    print(f"[info] Created combined corpus with {len(combined_corpus)} documents")
    
    vectorizer = build_vectorizer()
    print("[info] Fitting TF-IDF vectorizer on combined corpus...")
    vectorizer.fit(combined_corpus)
    print("[info] Vectorizer training complete")
    
    save_vectorizer(vectorizer)
    
    print("\n[info] Computing similarity scores...")
    val_scores = compute_similarity_scores(val_df, vectorizer)
    test_scores = compute_similarity_scores(test_df, vectorizer)
    print(f"[info] Computed {len(val_scores)} validation scores and {len(test_scores)} test scores")
    
    print("\n[info] Optimizing thresholds on validation set...")
    val_labels = val_df["label"].values
    best_potential, best_good, best_f1 = find_optimal_thresholds(
        val_scores, val_labels
    )
    print(f"[info] Optimal thresholds found:")
    print(f"[info]   Potential Fit Threshold: {best_potential:.4f}")
    print(f"[info]   Good Fit Threshold: {best_good:.4f}")
    print(f"[info]   Validation F1-score: {best_f1:.4f}")
    
    print("\n[info] Evaluating on test set...")
    test_labels = test_df["label"].values
    test_metrics = evaluate_thresholds(
        test_scores, test_labels, best_potential, best_good
    )
    
    print(f"\n[info] Test Set Results:")
    print(f"[info]   Accuracy: {test_metrics['accuracy']:.4f}")
    print(f"[info]   Weighted F1: {test_metrics['weighted_avg']['f1_score']:.4f}")
    print(f"[info]   Macro F1: {test_metrics['macro_avg']['f1_score']:.4f}")
    print(f"\n[info] Per-class metrics:")
    for label in CLASS_LABELS:
        metrics = test_metrics['per_class'][label]
        print(f"[info]   {label}:")
        print(f"[info]     Precision: {metrics['precision']:.4f}")
        print(f"[info]     Recall: {metrics['recall']:.4f}")
        print(f"[info]     F1-score: {metrics['f1_score']:.4f}")
        print(f"[info]     Support: {metrics['support']}")
    
    save_thresholds(best_potential, best_good, best_f1, test_metrics)
    
    print("\n[info] Training and optimization pipeline complete")


if __name__ == "__main__":
    main()
