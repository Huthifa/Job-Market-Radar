import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from skills import normalize_skills

FIELDS = ["seniority", "remote", "salary_min", "salary_max", "currency", "salary_period"]


def read_jsonl(path: str) -> list[dict]:
    """Read a JSONL file: one JSON object per line."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def field_accuracy(labels: dict, predictions: dict, field: str) -> float:
    """Share of postings where the AI's answer equals your label."""
    correct = 0
    for posting_id, label in labels.items():
        prediction = predictions.get(posting_id)
        if prediction is not None and prediction[field] == label[field]:
            correct += 1
    return correct / len(labels)


def skill_scores(labels: dict, predictions: dict) -> tuple[float, float]:
    """Precision and recall of the skills, over all postings together."""
    in_both = 0
    total_predicted = 0
    total_labeled = 0
    for posting_id, label in labels.items():
        prediction = predictions.get(posting_id)
        real = set(normalize_skills(label["skills"]))
        guessed = set(normalize_skills(prediction["skills"])) if prediction else set()
        in_both += len(real & guessed)
        total_predicted += len(guessed)
        total_labeled += len(real)
    precision = in_both / total_predicted if total_predicted else 0
    recall = in_both / total_labeled if total_labeled else 0
    return precision, recall


def show_mistakes(labels: dict, predictions: dict) -> None:
    """Print every disagreement, so you can see WHY the AI was wrong."""
    for posting_id, label in labels.items():
        prediction = predictions.get(posting_id)
        if prediction is None:
            print(f"\n{posting_id}: SKIPPED")
            continue
        problems = []
        for field in FIELDS:
            if prediction[field] != label[field]:
                problems.append(f"  {field}: you={label[field]!r}  ai={prediction[field]!r}")
        real = set(normalize_skills(label["skills"]))
        guessed = set(normalize_skills(prediction["skills"]))
        if guessed - real:
            problems.append(f"  skills the AI ADDED:  {sorted(guessed - real)}")
        if real - guessed:
            problems.append(f"  skills the AI MISSED: {sorted(real - guessed)}")
        if problems:
            print(f"\n{posting_id}")
            print("\n".join(problems))


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    labels = {row["id"]: row for row in read_jsonl(os.path.join("ai", "eval", "labels.jsonl"))}
    predictions = {
        row["id"]: row
        for row in read_jsonl(os.path.join("ai", "eval", f"predictions_{version}.jsonl"))
    }

    print(f"Prompt {version}: {len(predictions)} of {len(labels)} postings answered\n")
    for field in FIELDS:
        print(f"{field:15} {field_accuracy(labels, predictions, field):.0%}")
    precision, recall = skill_scores(labels, predictions)
    print(f"{'skills':15} precision {precision:.0%}, recall {recall:.0%}")

    if "--mistakes" in sys.argv:
        show_mistakes(labels, predictions)