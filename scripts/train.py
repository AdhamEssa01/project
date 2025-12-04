# scripts/train.py
"""
Train a TF-IDF vectorizer for cosine similarity-based job-CV matching.

This script:
    * loads the structured dataset in data/train.csv
    * cleans and normalizes the text fields
    * creates a combined corpus from all resume and job description texts
    * fits a TF-IDF vectorizer on the combined corpus
    * saves the trained vectorizer to saved_model/
"""

import os

import pandas as pd
from joblib import dump
from sklearn.feature_extraction.text import TfidfVectorizer

from app.preprocess import clean_text

DATA_PATH = os.path.join("data", "train.csv")
MODEL_DIR = "saved_model"
VECTORIZER_FILENAME = "job_match_pipeline.joblib"  # Keep same filename for compatibility



def load_and_preprocess_dataset(path: str) -> pd.DataFrame:
    """
    Load and preprocess the training dataset.
    
    Returns a DataFrame with cleaned resume and job description texts.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Training data not found at {path}")

    df = pd.read_csv(path)
    required_cols = {"resume_text", "job_description_text"}
    if not required_cols.issubset(df.columns):
        missing = ", ".join(sorted(required_cols - set(df.columns)))
        raise ValueError(f"train.csv missing required columns: {missing}")

    # Clean both text fields
    df["resume_clean"] = df["resume_text"].fillna("").apply(clean_text)
    df["job_clean"] = df["job_description_text"].fillna("").apply(clean_text)
    
    # Filter out empty texts
    df = df[(df["resume_clean"].str.len() > 0) & (df["job_clean"].str.len() > 0)]
    
    if df.empty:
        raise ValueError("No usable rows after cleaning.")

    return df[["resume_clean", "job_clean"]]


def build_vectorizer() -> TfidfVectorizer:
    """
    Create and configure a TF-IDF vectorizer.
    
    Returns:
        TfidfVectorizer configured with:
        - max_features=20000: Top 20,000 features by term frequency
        - ngram_range=(1, 2): Unigrams and bigrams
        - stop_words="english": Removes English stopwords
    """
    return TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2),
        stop_words="english",
    )


def create_combined_corpus(df: pd.DataFrame) -> list:
    """
    Create a combined corpus from all resume and job description texts.
    
    The corpus is created by concatenating (summing) all resume_text values
    and all job_description_text values into a single list. This ensures the
    TF-IDF vectorizer learns the vocabulary and IDF weights from the entire
    training dataset, providing a consistent feature space for both CV and
    job description vectors during inference.
    
    Args:
        df: DataFrame with 'resume_clean' and 'job_clean' columns
    
    Returns:
        List of all cleaned texts (resumes + job descriptions)
    """
    # Summation: Combine all resume texts and all job description texts
    # into a single corpus list. This is done by:
    # 1. Extracting all resume_clean values as a list
    # 2. Extracting all job_clean values as a list  
    # 3. Concatenating both lists together
    resume_texts = df["resume_clean"].tolist()
    job_texts = df["job_clean"].tolist()
    combined_corpus = resume_texts + job_texts
    return combined_corpus


def save_vectorizer(vectorizer: TfidfVectorizer) -> None:
    """
    Save the fitted TF-IDF vectorizer to disk.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    vectorizer_path = os.path.join(MODEL_DIR, VECTORIZER_FILENAME)
    dump(vectorizer, vectorizer_path)
    print(f"[info] Saved trained TF-IDF vectorizer to {vectorizer_path}")
    print(f"[info] Vocabulary size: {len(vectorizer.vocabulary_)} features")


def main():
    print("Training TF-IDF vectorizer for cosine similarity matching")
    
    # Load and preprocess dataset
    df = load_and_preprocess_dataset(DATA_PATH)
    print(f"[info] Loaded {len(df)} training examples")
    
    # Create combined corpus by summing all resume and job description texts
    # This corpus will be used to fit the TF-IDF vectorizer, ensuring it learns
    # the vocabulary and IDF weights from the entire training dataset
    combined_corpus = create_combined_corpus(df)
    print(f"[info] Created combined corpus with {len(combined_corpus)} documents")
    print(f"[info]   - {len(df)} resume texts")
    print(f"[info]   - {len(df)} job description texts")
    
    # Build and fit the TF-IDF vectorizer on the combined corpus
    vectorizer = build_vectorizer()
    print("[info] Fitting TF-IDF vectorizer on combined corpus...")
    vectorizer.fit(combined_corpus)
    print("[info] Training complete")
    
    # Save the fitted vectorizer
    save_vectorizer(vectorizer)


if __name__ == "__main__":
    main()
