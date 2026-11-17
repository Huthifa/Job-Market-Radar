import json
import os
from datetime import date

import requests

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"
RAW_DIR = os.path.join("data", "raw")


def fetch_remotive_jobs() -> list[dict]:
    """Ask Remotive for jobs and return the list of jobs."""
    response = requests.get(REMOTIVE_URL, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["jobs"]


def save_raw(jobs: list[dict], source: str) -> str:
    """Save jobs as JSON in data/raw/<source>_<today>.json and return the path."""
    os.makedirs(RAW_DIR, exist_ok=True)
    filename = f"{source}_{date.today().isoformat()}.json"
    path = os.path.join(RAW_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    return path


if __name__ == "__main__":
    jobs = fetch_remotive_jobs()
    path = save_raw(jobs, "remotive")
    print(f"Saved {len(jobs)} jobs to {path}")