import json
import os

SAMPLE = os.path.join("ai", "eval", "sample.jsonl")
LABELS = os.path.join("ai", "eval", "labels.jsonl")

SENIORITY = ["intern", "junior", "mid", "senior", "lead", "unknown"]
REMOTE = ["remote", "hybrid", "onsite", "unknown"]
PERIOD = ["hour", "month", "year", "unknown"]


def read_jsonl(path: str) -> list[dict]:
    """Read a JSONL file: one JSON object per line. Missing file = empty list."""
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def ask_choice(question: str, options: list[str]) -> str:
    """Keep asking until the answer is one of the allowed options."""
    while True:
        answer = input(f"{question} {options}: ").strip().lower()
        if answer in options:
            return answer
        print("  Not an option, try again.")


def ask_number(question: str) -> int | None:
    """Ask for a whole number. Blank means not stated."""
    while True:
        answer = input(f"{question} (number, blank = not stated): ").strip()
        if answer == "":
            return None
        try:
            return int(answer)
        except ValueError:
            print("  Numbers only, like 170000 (not 170k).")


def label_one(posting: dict) -> dict:
    """Show one posting and ask the 7 questions."""
    print("\n" + "=" * 80)
    print(f"{posting['id']}  |  {posting['title']}  |  {posting['company']}")
    print("-" * 80)
    print(posting["description"])
    print("-" * 80)

    skills_text = input("skills (comma-separated, blank = none): ")
    skills = [s.strip().lower() for s in skills_text.split(",") if s.strip()]
    seniority = ask_choice("seniority", SENIORITY)
    remote = ask_choice("remote", REMOTE)
    salary_min = ask_number("salary_min")
    salary_max = ask_number("salary_max")

    if salary_min is None and salary_max is None:
        currency = None
        salary_period = None
    else:
        currency = input("currency (USD, EUR, GBP...): ").strip().upper() or None
        salary_period = ask_choice("salary_period", PERIOD)

    return {
        "id": posting["id"],
        "skills": skills,
        "seniority": seniority,
        "remote": remote,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "currency": currency,
        "salary_period": salary_period,
    }


if __name__ == "__main__":
    sample = read_jsonl(SAMPLE)
    done = {row["id"] for row in read_jsonl(LABELS)}
    todo = [p for p in sample if p["id"] not in done]
    print(f"{len(done)} labeled, {len(todo)} to go. Ctrl+C to stop anytime; finished ones are saved.")

    for number, posting in enumerate(todo, start=len(done) + 1):
        print(f"\n[{number} / {len(sample)}]")
        label = label_one(posting)
        with open(LABELS, "a", encoding="utf-8") as f:
            f.write(json.dumps(label, ensure_ascii=False) + "\n")

    print("\nAll labeled!")