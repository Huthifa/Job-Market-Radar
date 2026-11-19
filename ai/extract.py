import json
import os
import sys
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from pydantic import ValidationError
from schema import Extraction
from skills import normalize_skills

load_dotenv()

MODEL = "gemini-3.5-flash-lite"
SAMPLE = os.path.join("ai", "eval", "sample.jsonl")
SECONDS_BETWEEN_CALLS = 5


def read_jsonl(path: str) -> list[dict]:
    """Read a JSONL file: one JSON object per line."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def build_prompt(template: str, posting: dict) -> str:
    """Put the posting's text into the prompt template."""
    text = posting["description"] or ""
    if posting["source"] == "remotive":
        text = f"Job title: {posting['title']}\n\n{text}"
    return template.replace("{posting}", text)


def extract(client, prompt: str) -> Extraction:
    """Ask the model once, and return its answer checked by pydantic."""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": Extraction,
        },
    )
    return Extraction.model_validate_json(response.text)


def extract_with_retry(client, prompt: str) -> Extraction | None:
    """Try twice. If both fail, give up and return None."""
    for attempt in (1, 2):
        try:
            return extract(client, prompt)
        except ValidationError as error:
            print(f"  attempt {attempt}: wrong shape ({error.error_count()} problems)")
        except errors.APIError as error:
            print(f"  attempt {attempt}: API error {error.code}, waiting 30s")
            time.sleep(30)
            continue
        time.sleep(SECONDS_BETWEEN_CALLS)
    return None


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    with open(os.path.join("ai", "prompts", f"extract_{version}.txt"), encoding="utf-8") as f:
        template = f.read()
    out_path = os.path.join("ai", "eval", f"predictions_{version}.jsonl")

    client = genai.Client()
    postings = read_jsonl(SAMPLE)
    saved = 0
    skipped = 0

    done = set()
    if os.path.exists(out_path):
        done = {row["id"] for row in read_jsonl(out_path)}
    todo = [p for p in postings if p["id"] not in done]
    print(f"{len(done)} already done, {len(todo)} to go")

    with open(out_path, "a", encoding="utf-8") as f:
        for number, posting in enumerate(todo, start=1):
            print(f"[{number}/{len(todo)}] {posting['id']}")
            result = extract_with_retry(client, build_prompt(template, posting))
            if result is None:
                print("  skipped after 2 tries")
                skipped = skipped + 1
            else:
                
                row = {"id": posting["id"], **result.model_dump()}
                row["skills"] = normalize_skills(row["skills"])
                if posting["source"] == "remotive":
                    row["remote"] = "remote"
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                saved = saved + 1
            time.sleep(SECONDS_BETWEEN_CALLS)

    print(f"\nSaved {saved}, skipped {skipped} → {out_path}")