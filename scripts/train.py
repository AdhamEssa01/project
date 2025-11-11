# scripts/train.py
"""
Comprehensive training script for Job Recommendation model
Supports training the model from:
(resume-job-description-fit) data - containing relationships between CVs and JDs
(job_pool_cleaned.csv and remotive_jobs.csv) data - containing job descriptions only, used as a job pool for later comparison

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
DATA_JOB_POOL_PATH = os.path.join("data", "job_pool_cleaned.csv")  # new dataset
DATA_REMOTIVE_JOBS_PATH = os.path.join("data", "remotive_jobs.csv")  # remotive jobs dataset
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
    """ Train the model from job pool data (job_pool_cleaned.csv and remotive_jobs.csv) """
    all_jobs = []
    all_meta = []
    job_id = 0

    # Read job_pool_cleaned.csv
    if os.path.exists(DATA_JOB_POOL_PATH):
        print("📂 Reading job_pool_cleaned.csv...")
        df1 = pd.read_csv(DATA_JOB_POOL_PATH)

        if "job_text" in df1.columns:
            # Clean columns
            df1["job_text"] = df1["job_text"].fillna("").apply(clean_text)
            df1["title"] = df1["title"].fillna("").apply(clean_text)
            df1["company"] = df1["company"].fillna("").apply(clean_text)
            df1["category"] = df1["category"].fillna("").apply(clean_text)
            df1["location"] = df1["location"].fillna("").apply(clean_text)

            # Filter out empty job texts
            df1 = df1[df1["job_text"].str.strip() != ""]

            for i in range(len(df1)):
                all_jobs.append(df1.loc[i, "job_text"])
                all_meta.append({
                    "id": job_id,
                    "title": df1.loc[i, "title"],
                    "company": df1.loc[i, "company"],
                    "category": df1.loc[i, "category"],
                    "location": df1.loc[i, "location"],
                })
                job_id += 1
            print(f"  ✓ Loaded {len(df1)} jobs from job_pool_cleaned.csv")
        else:
            print("  ⚠ The file does not contain the column job_text. Skipping.")
    else:
        print(f"  ⚠ File {DATA_JOB_POOL_PATH} not found. Skipping.")

    # Read remotive_jobs.csv
    if os.path.exists(DATA_REMOTIVE_JOBS_PATH):
        print("📂 Reading remotive_jobs.csv...")
        df2 = pd.read_csv(DATA_REMOTIVE_JOBS_PATH)

        if "description" in df2.columns:
            # Clean columns - remotive_jobs.csv uses 'description' instead of 'job_text'
            df2["description"] = df2["description"].fillna("").apply(clean_text)
            df2["title"] = df2["title"].fillna("").apply(clean_text)
            df2["company"] = df2["company"].fillna("").apply(clean_text)
            df2["category"] = df2["category"].fillna("").apply(clean_text)
            df2["location"] = df2["location"].fillna("").apply(clean_text)

            # Filter out empty descriptions
            df2 = df2[df2["description"].str.strip() != ""]

            for i in range(len(df2)):
                all_jobs.append(df2.loc[i, "description"])
                all_meta.append({
                    "id": job_id,
                    "title": df2.loc[i, "title"],
                    "company": df2.loc[i, "company"],
                    "category": df2.loc[i, "category"],
                    "location": df2.loc[i, "location"],
                })
                job_id += 1
            print(f"  ✓ Loaded {len(df2)} jobs from remotive_jobs.csv")
        else:
            print("  ⚠ The file does not contain the column description. Skipping.")
    else:
        print(f"  ⚠ File {DATA_REMOTIVE_JOBS_PATH} not found. Skipping.")

    if len(all_jobs) == 0:
        print("❌ No jobs found in any of the data files!")
        return

    print(f"\n📊 Total number of jobs: {len(all_jobs)}")

    # Train the model
    matcher = TfidfJobMatcher(max_features=10000, stop_words="english")

    print("Training TF-IDF model on job data...")
    matcher.fit(job_texts=all_jobs, job_meta=all_meta)
    matcher.save(SAVE_PATH)

    print(f"Model successfully trained and saved in {SAVE_PATH}")
    print(f"Number of jobs used: {len(all_jobs)}")


# ----------------------------------------
# Entry point
# ----------------------------------------

def main():
    print("Job Recommendation Model Training Script")
    print("Select training type:")
    print("1. Train from resume-job-description-fit dataset")
    print("2. Train from job_pool_cleaned.csv and remotive_jobs.csv (jobs only)")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        train_from_resume_jd()
    elif choice == "2":
        train_from_job_pool()
    else:
        print("Invalid choice. Please restart and enter 1 or 2.")

if __name__ == "__main__":
    main()
