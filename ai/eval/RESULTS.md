# Extraction results

**Test set:** 30 hand-labeled postings (5 Remotive + 25 Hacker News, picked at random with seed 42).
Labels follow `LABELING_RULES.md`.
**Model:** `gemini-3.5-flash-lite` (free tier), structured output with a pydantic schema.

## Scores per prompt version

| Prompt | Seniority | Remote | Sal. min | Sal. max | Currency | Period | Skills P | Skills R |
|---|---|---|---|---|---|---|---|---|
| v1 | 97% | 90% | 97% | 93% | 97% | 93% | 67% | 84% |
| v1 + skill names | 97% | 90% | 97% | 93% | 97% | 93% | 74% | 92% |
| v2 | 93% | 97% | 100% | 93% | 100% | 100% | 94% | 77% |
| v3 | 97% | 93% | 100% | 100% | 100% | 100% | 89% | 93% |

P = precision (of the skills the AI listed, how many were right).
R = recall (of the real skills, how many the AI found).

## What changed between versions

- **v1:** simple prompt, with the main rule for each field.
- **v1 + skill names:** no new AI calls. Added a skill-name alias map (`ai/skills.py`), so
  "Apache Airflow" and "airflow" count as the same skill. Most of v1's "missed" skills were just spelling.
- **v2:** added rules for the traps found in v1's mistakes: other roles' skills, the company's
  product vs. the role, not-a-job-ad posts, general areas, URLs, salary edge cases.
  Precision jumped, but the AI became too strict and dropped real skills, so recall fell.
- **v3:** said what DOES count as a skill (nice-to-haves, the team's stack, hardware), softened the
  strict line, and fixed "$80k + equity" being read as "80k+". The best balance.

## Notes

- **One label was wrong** (posting 50370710 said "Remote"). It was found in error analysis and
  fixed before comparing versions. All rows above use the corrected labels.
- **Small test set:** each posting is worth about 3%, so differences of 3–4% are one posting.
- **Remaining errors are mostly ambiguous:** "remote-first hybrid", vendor names (Claude, OpenAI),
  "Senior/Staff" titles. Several are arguably not AI errors.
- **Risk of overfitting:** the prompts were tuned on these same 30 postings. The planned
  50-posting set will show whether v3 holds up on new ones.
- **Reliability:** the free tier returned HTTP 503 on roughly 1 in 3 requests; the retry and
  resume logic handled it, but it's a risk for the scheduled daily run.