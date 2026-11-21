import os
import sys

import psycopg
from db import DATABASE_URL
from embed import MAX_CHARS, embed_texts, to_pgvector
from extract import MODEL as LLM_MODEL
from google import genai
from pypdf import PdfReader
from schema import CvSkills
from skills import normalize_skills

CANDIDATES = 50
TOP_N = 10
VECTOR_WEIGHT = 0.5
SKILL_WEIGHT = 0.5

NEAREST_JOBS = """
SELECT p.id, p.title, p.company, p.skills, 1 - (e.embedding <=> %(cv)s::vector) AS vector_score
FROM posting_embeddings e
JOIN postings p ON p.id = e.posting_id
ORDER BY e.embedding <=> %(cv)s::vector
LIMIT %(limit)s
"""


def read_cv_text(path: str) -> str:
    """Get the plain text out of a PDF or .txt CV."""
    if path.lower().endswith(".pdf"):
        reader = PdfReader(path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    text = text.strip()
    if not text:
        raise ValueError("Could not read text from the CV")
    return text


def cv_skills(client, cv_text: str) -> list[str]:
    """Ask Gemini which technical skills the CV shows."""
    with open(os.path.join("ai", "prompts", "cv_skills_v1.txt"), encoding="utf-8") as f:
        prompt = f.read().replace("{cv}", cv_text[:MAX_CHARS])
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config={"response_mime_type": "application/json", "response_schema": CvSkills},
    )
    return normalize_skills(CvSkills.model_validate_json(response.text).skills)


def score_job(cv_skill_set: set[str], job_skills: list[str], vector_score: float) -> dict:
    """Mix meaning and skill overlap into one score, and list matching/missing skills."""
    job_skill_set = set(job_skills)
    matching = sorted(job_skill_set & cv_skill_set)
    missing = sorted(job_skill_set - cv_skill_set)
    overlap = len(matching) / len(job_skill_set) if job_skill_set else 0.0
    score = VECTOR_WEIGHT * vector_score + SKILL_WEIGHT * overlap
    return {
        "score": score,
        "vector_score": vector_score,
        "skill_overlap": overlap,
        "matching_skills": matching,
        "missing_skills": missing,
    }


def match_cv(conn, client, cv_text: str, limit: int = TOP_N) -> tuple[list[str], list[dict]]:
    """Return the CV's skills and the best-matching jobs, best first."""
    skills = set(cv_skills(client, cv_text))
    cv_vector = embed_texts(client, [cv_text[:MAX_CHARS]], "RETRIEVAL_QUERY")[0]
    rows = conn.execute(NEAREST_JOBS, {"cv": to_pgvector(cv_vector), "limit": CANDIDATES}).fetchall()

    results = []
    for posting_id, title, company, job_skills, vector_score in rows:
        result = score_job(skills, job_skills, vector_score)
        result.update({"id": posting_id, "title": title, "company": company})
        results.append(result)

    results.sort(key=lambda r: r["score"], reverse=True)
    return sorted(skills), results[:limit]


if __name__ == "__main__":
    text = read_cv_text(sys.argv[1])
    client = genai.Client()
    with psycopg.connect(DATABASE_URL) as conn:
        skills, matches = match_cv(conn, client, text)

    print(f"CV skills: {', '.join(skills)}\n")
    for rank, m in enumerate(matches, start=1):
        print(
            f"#{rank}  {m['score']:.2f}  (meaning {m['vector_score']:.2f}, "
            f"skills {m['skill_overlap']:.0%})  {m['title']} @ {m['company']}"
        )
        print(f"     have:    {', '.join(m['matching_skills']) or '-'}")
        print(f"     missing: {', '.join(m['missing_skills']) or '-'}")