# scripts/fetch_jobs_from_api.py
import requests
import pandas as pd
import os

JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY", "2b0fa333-08bd-4f0b-9f28-7e2757315622")

COUNTRY = "eg"
LIMIT = 50

def fetch_jobs_from_jooble(query, country=COUNTRY, limit=LIMIT):
    """Fetch jobs from Jooble API for a given query"""
    url = f"https://{country}.jooble.org/api/{JOOBLE_API_KEY}"
    payload = {"keywords": query, "page": 1}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Request error for query '{query}': {e}")
        return []

    if response.status_code != 200:
        print(f"API Error for query '{query}': {response.status_code}")
        print(response.text)
        return []

    try:
        data = response.json()
        jobs = data.get("jobs", [])
        print(f"  Found {len(jobs)} jobs from API")
    except Exception as e:
        print(f"Error parsing response for query '{query}': {e}")
        return []

    records = []
    for job in jobs[:limit]:
        records.append({
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "snippet": job.get("snippet", ""),
            "link": job.get("link", ""),
            "salary": job.get("salary", ""),
        })
    print(f"  Processed {len(records)} jobs for query '{query}'")
    return records

def main():
    queries = ["software engineer", "backend developer", "data analyst", "cybersecurity", "machine learning"]
    all_jobs = []

    print("=" * 50)
    print("Fetching jobs from Jooble API")
    print("=" * 50)
    
    for q in queries:
        print(f"\nFetching jobs for: {q}")
        jobs = fetch_jobs_from_jooble(query=q)
        if jobs:
            all_jobs.extend(jobs)
            print(f"  ✓ Added {len(jobs)} jobs")
        else:
            print(f"  ✗ No jobs found for '{q}'")

    if not all_jobs:
        print("\n" + "=" * 50)
        print("ERROR: No jobs were fetched from the API!")
        print("Possible reasons:")
        print("  1. API key might be invalid or expired")
        print("  2. API endpoint might be incorrect")
        print("  3. Network connectivity issues")
        print("  4. No jobs available for the given queries")
        print("=" * 50)
        return

    print("\n" + "=" * 50)
    print(f"Total jobs fetched: {len(all_jobs)}")
    print("=" * 50)
    
    df = pd.DataFrame(all_jobs)
    
    # Show sample of data
    if len(df) > 0:
        print("\nSample of fetched jobs:")
        print(df.head(5).to_string())
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    save_path = os.path.join("data", "real_jobs.csv")
    
    # Save to CSV
    try:
        df.to_csv(save_path, index=False, encoding="utf-8")
        print(f"\n✓ Successfully saved {len(df)} jobs to {save_path}")
        print(f"  File size: {os.path.getsize(save_path)} bytes")
    except Exception as e:
        print(f"\n✗ Error saving file: {e}")
        return
    
    print("\n" + "=" * 50)
    print("Job fetching completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()
