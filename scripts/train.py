# scripts/train.py
"""
Comprehensive training script for Job Recommendation model
Supports training the model from:
(resume-job-description-fit) data - containing relationships between CVs and JDs
(job_pool_cleaned.csv) data - containing job descriptions only, used as a job pool for later comparison

The script cleans the data, builds a TF-IDF model, and saves it in the saved_model/ folder.
"""

import pandas as pd
import os
from app.preprocess import clean_text
from app.model import TfidfJobMatcher


# ----------------------------------------
# Paths setup
# ----------------------------------------
DATA_RESUME_JD_PATH = os.path.join("data", "cleaned_train.csv")  # old dataset
# DATA_JOB_POOL_PATH = os.path.join("data", "job_pool_cleaned.csv")  # new dataset
DATA_JOB_POOL_PATH = os.path.join("data", "job_pool_cleaned.csv")  # new dataset
SAVE_PATH = "saved_model"


# ----------------------------------------
# Helper functions
# ----------------------------------------

def train_from_resume_jd():
    """ Train the model from the dataset containing (resume + job description) """
    if not os.path.exists(DATA_RESUME_JD_PATH):
        print(f"File {DATA_RESUME_JD_PATH} not found.")
        return

    print("Reading resume-job-description-fit data...")
    df = pd.read_csv(DATA_RESUME_JD_PATH)

    if "job_clean" not in df.columns:
        print("The file does not contain the column job_clean.")
        return

    jobs = df["job_clean"].dropna().astype(str).tolist()
    meta = [{"index": i, "label": df.loc[i, "label"] if "label" in df.columns else "unknown"} for i in range(len(jobs))]

    print(f"Number of samples: {len(jobs)}")

    # Create the model
    matcher = TfidfJobMatcher(max_features=7000, stop_words="english")

    print("Training the model from resume and job description data...")
    matcher.fit(job_texts=jobs, job_meta=meta)
    matcher.save(SAVE_PATH)

    print(f"Model saved in {SAVE_PATH}")


def train_from_job_pool():
    """ Train the model from job pool data only (Job Posting.csv) """
    if not os.path.exists(DATA_JOB_POOL_PATH):
        print(f"File {DATA_JOB_POOL_PATH} not found.")
        return

    print("📂 Reading job data...")
    df = pd.read_csv(DATA_JOB_POOL_PATH)

    if "job_text" not in df.columns:
        print("The file does not contain the column job_text. Make sure to run prepare_job_postings.py first.")
        return

    print(f"Number of jobs: {len(df)}")

    # Clean columns
    df["job_text"] = df["job_text"].fillna("").apply(clean_text)
    df["title"] = df["title"].fillna("").apply(clean_text)
    df["company"] = df["company"].fillna("").apply(clean_text)
    df["category"] = df["category"].fillna("").apply(clean_text)
    df["location"] = df["location"].fillna("").apply(clean_text)

    # Prepare texts and metadata
    jobs = df["job_text"].tolist()
    meta = [
        {
            "id": i,
            "title": df.loc[i, "title"],
            "company": df.loc[i, "company"],
            "category": df.loc[i, "category"],
            "location": df.loc[i, "location"],
        }
        for i in range(len(df))
    ]

    # Train the model
    matcher = TfidfJobMatcher(max_features=10000, stop_words="english")

    print("Training TF-IDF model on job data...")
    matcher.fit(job_texts=jobs, job_meta=meta)
    matcher.save(SAVE_PATH)

    print(f"Model successfully trained and saved in {SAVE_PATH}")
    print(f"Number of jobs used: {len(jobs)}")


# ----------------------------------------
# Entry point
# ----------------------------------------

def main():
    print("Job Recommendation Model Training Script")
    print("Select training type:")
    print("Train from resume-job-description-fit dataset")
    print("Train from job_pool_cleaned.csv (jobs only)")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        train_from_resume_jd()
    elif choice == "2":
        train_from_job_pool()
    else:
        print("Invalid choice. Please restart and enter 1 or 2.")

if __name__ == "__main__":
    main()
