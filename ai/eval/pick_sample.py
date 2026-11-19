import glob
import json
import os
import random

CLEAN_FILES = os.path.join("data", "clean", "postings_*.json")
OUT_PATH = os.path.join("ai", "eval", "sample.jsonl")

# 1. find the newest clean file
newest = sorted(glob.glob(CLEAN_FILES))[-1]

# 2. load it
with open(newest, encoding="utf-8") as f:
    postings = json.load(f)

# 3. split by source
remotive = [p for p in postings if p["source"] == "remotive"]
hackernews = [p for p in postings if p["source"] == "hackernews"]
# 4 + 5. pick at random, the same way every time
random.seed(42)
picked = random.sample(remotive, 5) + random.sample(hackernews, 25)

# 6. write one posting per line
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    for p in picked:
        row = {
            "id": p["id"],
            "source": p["source"],
            "title": p["title"],
            "company": p["company"],
            "description": p["description"],
        }
    
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

# 7. receipt
print(f"Saved {len(picked)} postings to {OUT_PATH}")