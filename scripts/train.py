# scripts/train.py
"""
Train a supervised resume/job description fit classifier.

This script:
    * loads the structured dataset in data/train.csv
    * cleans and normalizes the text fields and labels
    * trains a TF-IDF + Logistic Regression text pair classifier
    * evaluates the model on a hold-out set
    * saves the trained pipeline and evaluation report into saved_model/
"""

import json
import os
from typing import List, Optional, Tuple

import pandas as pd
from joblib import dump
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.preprocess import clean_text

DATA_PATH = os.path.join("data", "train.csv")
MODEL_DIR = "saved_model"
PIPELINE_FILENAME = "job_match_pipeline.joblib"
EVAL_FILENAME = "evaluation.json"
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


def load_dataset(path: str) -> pd.DataFrame:
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
    df["pair_text"] = (df["resume_clean"] + " [SEP] " + df["job_clean"]).str.strip()

    before = len(df)
    df = df.dropna(subset=["label_normalized"])
    df = df[df["pair_text"].str.len() > 0]
    if df.empty:
        raise ValueError("No usable rows after cleaning/normalization.")

    dropped = before - len(df)
    if dropped:
        print(f"[warn] Dropped {dropped} rows due to missing labels or empty text.")

    return df[["pair_text", "label_normalized"]].rename(
        columns={"pair_text": "text_pair", "label_normalized": "label"}
    )


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=20000,
                    ngram_range=(1, 2),
                    stop_words="english",
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000,
                    solver="lbfgs",
                ),
            ),
        ]
    )


def evaluate_model(
    pipeline: Pipeline, X_test: List[str], y_test: List[str]
) -> Tuple[float, dict]:
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(
        y_test,
        y_pred,
        labels=CLASS_LABELS,
        zero_division=0,
        output_dict=True,
    )
    return accuracy, report


def save_artifacts(pipeline: Pipeline, eval_report: dict) -> None:
    os.makedirs(MODEL_DIR, exist_ok=True)
    pipeline_path = os.path.join(MODEL_DIR, PIPELINE_FILENAME)
    dump(pipeline, pipeline_path)
    print(f"[info] Saved trained pipeline to {pipeline_path}")

    report_path = os.path.join(MODEL_DIR, EVAL_FILENAME)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(eval_report, f, indent=2)
    print(f"[info] Saved evaluation report to {report_path}")


def main():
    print("Training supervised Job Fit classifier")
    df = load_dataset(DATA_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        df["text_pair"],
        df["label"],
        test_size=0.2,
        random_state=42,
        stratify=df["label"],
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    print("Training complete")

    accuracy, report = evaluate_model(pipeline, X_test, y_test)
    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(json.dumps(report, indent=2))

    save_artifacts(
        pipeline,
        {
            "accuracy": accuracy,
            "report": report,
            "classes": list(pipeline.classes_),
        },
    )


if __name__ == "__main__":
    main()
