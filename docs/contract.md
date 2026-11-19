# Interface contract

This file is the agreement between the cloud side and the AI side. If you change a table, a column, an
endpoint or an environment variable, change this file in the same PR, and the other person must approve.

Status: **draft — decisions marked ⚠️ need both of us to agree.**

## 1. Data flow

```
Remotive API ─┐
              ├─► fetcher ─► raw_postings ─► clean ─► postings ─► LLM extraction ─► postings (skills, seniority, salary…)
HN "Who's     ┘                                                       │
Hiring"                                                               └─► embeddings ─► posting_embeddings
                                                                                              │
                         API (FastAPI) ◄──────────── reads postings + posting_embeddings ─────┘
                           │      ▲
                 dashboard ┘      └── POST /match-cv writes cv_matches
```

- **Writers:** the AI pipeline (fetcher → clean → extract → embed) writes `raw_postings`, `postings` and
  `posting_embeddings`. The API writes only `cv_matches`.
- **Readers:** the API and the dashboard. The dashboard talks only to the API, never to the database.
- **Schedule:** the pipeline runs once a day as a scheduled ECS task (Day 5). It must be safe to re-run:
  every write is an upsert keyed on `id`.

## 2. Job posting (JSON)

This is the shape of one posting everywhere it travels as JSON: API responses and pipeline files.

```json
{
  "id": "hackernews:50370710",
  "source": "hackernews",
  "url": "https://news.ycombinator.com/item?id=50370710",
  "title": "Senior Backend Engineer",
  "company": "Acme",
  "location": "Berlin, Germany",
  "remote": "hybrid",
  "posted_at": "2026-11-03T14:22:00Z",
  "description": "We're hiring…",
  "skills": ["python", "postgresql", "aws"],
  "seniority": "senior",
  "salary_min": 80000,
  "salary_max": 100000,
  "currency": "EUR",
  "salary_period": "year"
}
```

| Field | Type | Allowed values / notes |
|---|---|---|
| `id` | string | `"<source>:<source id>"`, e.g. `remotive:1234`, `hackernews:50370710` |
| `source` | string | `remotive` \| `hackernews` |
| `url` | string | link to the original posting |
| `title`, `company`, `location` | string \| null | cleaned text |
| `remote` | string | `remote` \| `hybrid` \| `onsite` \| `unknown` |
| `posted_at` | string \| null | ISO 8601, UTC |
| `description` | string \| null | HTML stripped |
| `skills` | string[] | lowercase, normalised through `ai/skills.py` (`"Apache Airflow"` → `"airflow"`) |
| `seniority` | string | `intern` \| `junior` \| `mid` \| `senior` \| `lead` \| `unknown` |
| `salary_min`, `salary_max` | integer \| null | whole currency units, no `k` |
| `currency` | string \| null | ISO 4217 code, e.g. `USD`, `EUR` |
| `salary_period` | string \| null | `hour` \| `month` \| `year` \| `unknown` |

The allowed values match the pydantic model in `ai/schema.py`. That model is the source of truth.

## 3. Database (Postgres 17 + pgvector)

### `raw_postings` — untouched source data, for re-processing

| Column | Type | Notes |
|---|---|---|
| `id` | TEXT PRIMARY KEY | same format as `postings.id` |
| `source` | TEXT NOT NULL | |
| `fetched_at` | TIMESTAMPTZ NOT NULL DEFAULT now() | |
| `data` | JSONB NOT NULL | the source's JSON as received |

### `postings` — one cleaned, enriched posting per row

| Column | Type | Notes |
|---|---|---|
| `id` | TEXT PRIMARY KEY | |
| `source` | TEXT NOT NULL | |
| `url` | TEXT NOT NULL | |
| `title`, `company`, `location` | TEXT | |
| `remote` | TEXT NOT NULL DEFAULT 'unknown' | ⚠️ **currently `BOOLEAN` in `ai/db.py`; must change to TEXT** (see §6) |
| `posted_at` | TIMESTAMPTZ | |
| `description` | TEXT | |
| `skills` | TEXT[] NOT NULL DEFAULT '{}' | GIN index for "jobs with skill X" |
| `seniority` | TEXT | |
| `salary_min`, `salary_max` | INTEGER | ⚠️ currently `NUMERIC`; integer matches the pydantic model |
| `currency` | TEXT | |
| `salary_period` | TEXT | ⚠️ **missing from `ai/db.py`; must be added** |
| `extracted_at` | TIMESTAMPTZ | null = not yet processed by the LLM; lets the pipeline skip done rows |
| `extraction_version` | TEXT | e.g. `v3`, so we know which prompt produced the row |

### `posting_embeddings` — one vector per posting (Day 3)

| Column | Type | Notes |
|---|---|---|
| `posting_id` | TEXT PRIMARY KEY REFERENCES postings(id) ON DELETE CASCADE | |
| `model` | TEXT NOT NULL | embedding model name |
| `embedding` | vector(⚠️ N) NOT NULL | ⚠️ N set by the AI engineer's model choice. Keep **N ≤ 2000**: pgvector's HNSW index doesn't support more dimensions for `vector`. |
| `created_at` | TIMESTAMPTZ NOT NULL DEFAULT now() | |

Index: `CREATE INDEX ON posting_embeddings USING hnsw (embedding vector_cosine_ops);`

### `cv_matches` — results of each CV match (Day 3–4)

| Column | Type | Notes |
|---|---|---|
| `id` | BIGSERIAL PRIMARY KEY | |
| `match_id` | UUID NOT NULL | one value per `/match-cv` request, shared by its rows |
| `created_at` | TIMESTAMPTZ NOT NULL DEFAULT now() | |
| `posting_id` | TEXT NOT NULL REFERENCES postings(id) ON DELETE CASCADE | |
| `rank` | SMALLINT NOT NULL | 1 = best |
| `score` | REAL NOT NULL | final combined score, 0–1 |
| `vector_score` | REAL NOT NULL | cosine similarity |
| `skill_overlap` | REAL NOT NULL | share of the posting's skills found in the CV |
| `matching_skills` | TEXT[] NOT NULL | |
| `missing_skills` | TEXT[] NOT NULL | |

⚠️ **We do not store the CV text or file.** CVs contain personal data; only the match results are kept.

### Schema ownership

⚠️ Proposal: until Day 4, the `CREATE TABLE` statements live in `ai/db.py`. On Day 4 they move into
migrations (Alembic, in `api/`), which are run against RDS. From then on, only migrations change the schema.

## 4. API endpoints

Base URL: `http://localhost:8000` locally; the load balancer URL on AWS (Day 4).
Errors use FastAPI's default shape: `{"detail": "message"}` with the matching HTTP status.

### `GET /health`
Liveness check for Docker and the load balancer. No database access.
```json
200 {"status": "ok"}
```

### `GET /jobs`
List postings, newest first.

Query params (all optional): `skill` (repeatable, all must match), `seniority`, `remote`, `source`,
`limit` (default 20, max 100), `offset` (default 0).

```json
200 {
  "total": 1342,
  "limit": 20,
  "offset": 0,
  "items": [ <job posting, §2>, … ]
}
```

### `GET /jobs/{id}/similar`
The postings most similar to one posting, by embedding.

Query params: `limit` (default 10, max 50).
```json
200 {
  "id": "hackernews:50370710",
  "items": [ {"score": 0.91, "job": <job posting>}, … ]
}
404 {"detail": "Job not found"}
```

### `GET /stats/skills`
Most-requested skills, for the dashboard.

Query params: `limit` (default 20), `since` (ISO date, optional), `seniority` (optional).
```json
200 {
  "total_postings": 1342,
  "items": [ {"skill": "python", "count": 512, "share": 0.38}, … ]
}
```

### `POST /match-cv`
Match a CV to postings.

Request: `multipart/form-data` with field `file` (PDF, max 5 MB). Query param `limit` (default 10, max 50).
```json
200 {
  "match_id": "6f1c…",
  "cv_skills": ["python", "docker", "aws"],
  "items": [
    {
      "rank": 1,
      "score": 0.87,
      "vector_score": 0.82,
      "skill_overlap": 0.75,
      "matching_skills": ["python", "aws"],
      "missing_skills": ["kubernetes"],
      "job": <job posting>
    }, …
  ]
}
400 {"detail": "File must be a PDF"}
413 {"detail": "File too large"}
422 {"detail": "Could not read text from the PDF"}
```

## 5. Environment variables

| Variable | Used by | Local | AWS (Day 4) |
|---|---|---|---|
| `DATABASE_URL` | api, fetcher | built in `docker-compose.yml` | built from Secrets Manager |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | db, compose | `.env` | Secrets Manager |
| `GEMINI_API_KEY` | fetcher (extraction, embeddings), api (`/match-cv`) | `.env` | Secrets Manager |
| `API_BASE_URL` | dashboard | `http://api:8000` | load balancer URL |

`.env.example` lists every variable with a fake value. Add new ones there too.

## 6. Known mismatches to fix (Day 3)

1. `postings.remote` is `BOOLEAN` in `ai/db.py`, but extraction returns `remote | hybrid | onsite | unknown`,
   and `clean.py` sets `True` for Remotive. → change the column to TEXT and the cleaner to `"remote"`.
2. `salary_period` is extracted but has no column. → add it.
3. Extraction writes `ai/eval/predictions_*.jsonl`, not the database. → the pipeline needs a step that
   updates `postings` with the extraction results and sets `extracted_at`.
4. `salary_min` / `salary_max` are `NUMERIC` in the database but `int` in pydantic. → pick INTEGER.

