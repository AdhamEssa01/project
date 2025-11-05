# scripts/train.py
"""
مثال سكربت تدريب يمكن استخدامه لاحقًا عندما يكون لديك مجموعة بيانات فعلية (CSV/JSON).
هذا الملف الآن يوضّح كيف تبني موديل ثم تحفظه باستخدام TfidfJobMatcher.save(path).
"""
import pandas as pd
from app.preprocess import clean_text
from app.model import TfidfJobMatcher
import os

DATA_PATH = os.path.join("data", "cleaned_train.csv")

def load_jobs_from_cleaned_csv(csv_path):
    df = pd.read_csv(csv_path)
    jobs = df['job_clean'].dropna().astype(str).unique().tolist()
    return jobs, [{"index": i} for i in range(len(jobs))]


def main():
    jobs, meta = load_jobs_from_cleaned_csv(DATA_PATH)
    matcher = TfidfJobMatcher(max_features=7000, stop_words='english')
    matcher.fit(job_texts=jobs, job_meta=meta)
    matcher.save("saved_model")


if __name__ == "__main__":
    main()
