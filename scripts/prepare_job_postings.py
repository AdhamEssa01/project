# scripts/prepare_job_postings.py
import pandas as pd
import os
import re
from app.preprocess import clean_text

DATA_PATH = os.path.join("data", "Job Posting.csv")
SAVE_PATH = os.path.join("data", "job_pool_cleaned.csv")

def extract_company(domain):
    if pd.isna(domain):
        return None
    domain = str(domain).lower()
    domain = re.sub(r"^www\.|\.com|\.co|\.org|\.net|\.io", "", domain)
    parts = domain.split(".")
    return parts[0] if parts else domain

def main():
    if not os.path.exists(DATA_PATH):
        print("File does not exist:", DATA_PATH)
        return

    print("Reading the file ...")
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(DATA_PATH, encoding="latin1")

    expected_cols = ["Job Opening Title", "Description", "Category", "Location", "Website Domain"]
    for col in expected_cols:
        if col not in df.columns:
            print(f"Column '{col}' is not found in the data file.")
    
    df_clean = pd.DataFrame()
    df_clean["title"] = df["Job Opening Title"] if "Job Opening Title" in df.columns else pd.Series([""] * len(df))
    df_clean["job_text"] = df["Description"] if "Description" in df.columns else pd.Series([""] * len(df))
    df_clean["category"] = df["Category"] if "Category" in df.columns else pd.Series([""] * len(df))
    df_clean["location"] = df["Location"] if "Location" in df.columns else pd.Series([""] * len(df))
    df_clean["company"] = df["Website Domain"].apply(extract_company) if "Website Domain" in df.columns else pd.Series([""] * len(df))

    print("Cleaning the text")
    df_clean["title"] = df_clean["title"].fillna("").apply(clean_text)
    df_clean["job_text"] = df_clean["job_text"].fillna("").apply(clean_text)
    df_clean["category"] = df_clean["category"].fillna("").apply(clean_text)
    df_clean["location"] = df_clean["location"].fillna("").apply(clean_text)
    df_clean["company"] = df_clean["company"].fillna("").apply(clean_text)

    df_clean = df_clean[df_clean["job_text"].str.strip() != ""].reset_index(drop=True)

    os.makedirs("data", exist_ok=True)
    df_clean.to_csv(SAVE_PATH, index=False, encoding="utf-8")

    print(f"{len(df_clean)} Done.")
    print(f"File is saved in: {SAVE_PATH}")

if __name__ == "__main__":
    main()
