# scripts/fetch_jobs_from_remotive.py
import requests
import pandas as pd
import os

def fetch_jobs_from_remotive():
    """
    جلب وظائف حقيقية من Remotive API (بدون مفتاح)
    """
    url = "https://remotive.com/api/remote-jobs"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Error fetching data: {response.status_code}")
        return []

    data = response.json()
    jobs = data.get("jobs", [])
    print(f"✅ عدد الوظائف اللي تم جلبها: {len(jobs)}")

    job_list = []
    for job in jobs:
        job_list.append({
            "title": job.get("title", ""),
            "company": job.get("company_name", ""),
            "category": job.get("category", ""),
            "location": job.get("candidate_required_location", ""),
            "description": job.get("description", ""),
            "url": job.get("url", "")
        })

    return job_list


def main():
    print("📡 جاري جلب الوظائف من Remotive...")
    jobs = fetch_jobs_from_remotive()

    if not jobs:
        print("⚠️ لم يتم العثور على وظائف. تأكد من الاتصال بالإنترنت.")
        return

    df = pd.DataFrame(jobs)

    os.makedirs("data", exist_ok=True)
    save_path = os.path.join("data", "remotive_jobs.csv")
    df.to_csv(save_path, index=False, encoding="utf-8")

    print(f"✅ تم حفظ {len(df)} وظيفة حقيقية في {save_path}")
    print("📊 أمثلة على أول 5 وظائف:")
    print(df.head(5))


if __name__ == "__main__":
    main()
