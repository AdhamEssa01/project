# scripts/prepare_resume_fit.py
import pandas as pd
from app.preprocess import clean_text
import os

DATA_PATH = os.path.join("data", "train.csv")
SAVE_PATH = os.path.join("data", "cleaned_train.csv")

def main():
    if not os.path.exists(DATA_PATH):
        print("Data is not found", DATA_PATH)
        return

    df = pd.read_csv(DATA_PATH)

    if 'resume_text' not in df.columns or 'job_description_text' not in df.columns:
        print("file has no required columns 'resume_text' or 'job_description_text'")
        return

    df["resume_clean"] = df["resume_text"].fillna("").apply(clean_text)
    df["job_clean"] = df["job_description_text"].fillna("").apply(clean_text)

    df[["resume_clean", "job_clean", "label"]].to_csv(SAVE_PATH, index=False)
    print(f"file is saved{SAVE_PATH}")

if __name__ == "__main__":
    main()
