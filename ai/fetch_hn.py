import requests

from fetch import save_raw

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"


def find_latest_hiring_thread() -> str:
    """Return the id of the newest 'Ask HN: Who is hiring?' thread."""
    response = requests.get(
        HN_SEARCH_URL,
        params={"tags": "story,author_whoishiring", "hitsPerPage": 10},
        timeout=30,
    )
    response.raise_for_status()

    for hit in response.json()["hits"]:
        if hit["title"].startswith("Ask HN: Who is hiring?"):
            return hit["objectID"]

    raise ValueError("Couldn't find a 'Who is hiring?' thread")


def fetch_hn_jobs(thread_id: str) -> list[dict]:
    """Return the job posts (top-level comments) from a thread."""
    response = requests.get(f"https://hn.algolia.com/api/v1/items/{thread_id}", timeout=30)
    response.raise_for_status()
    thread = response.json()

    jobs = []
    for comment in thread["children"]:
        if comment["text"]:
            jobs.append(comment)
    return jobs


if __name__ == "__main__":
    thread_id = find_latest_hiring_thread()
    print("Thread id:", thread_id)
    jobs = fetch_hn_jobs(thread_id)
    path = save_raw(jobs, "hackernews")
    print(f"Saved {len(jobs)} jobs to {path}")