
# Job Market Radar

A platform that fetches tech job postings daily, extracts skills with an LLM, and matches a CV to jobs.
Built in 7 days by two people who are here to **learn**:

- **Cloud engineer (Huthifa):** `infra/`, `.github/workflows/`, Docker, AWS, monitoring.
- **AI engineer (koopticon):** `ai/`, `dashboard/`, extraction, embeddings, matching, evaluation.
- **Shared:** `api/`, `docs/contract.md`.

The interface between the two halves is `docs/contract.md`. Read it before touching the database or the API.

## How to work with us (most important)

We are learning. The goal is that we understand everything in this repo, not that it gets written fast.

1. **Explain before writing.** Before you write code, explain the concept and the approach in a few sentences, then wait.
2. **Don't write whole files unless asked.** Prefer pointing at what to change, or writing small pieces.
3. **We write the core logic ourselves.** Cloud: security groups, IAM policies, Terraform structure. AI: prompts, evaluation logic, matching logic. You may review these, explain them and point out mistakes, but don't write them for us.
4. **Boilerplate is fine.** Config files, Dockerfiles we've already written once, test scaffolding, repetitive Terraform blocks: go ahead when asked.
5. **Review, don't rubber-stamp.** When we ask for a review, point out real problems, including security and cost.
6. **Never run anything we can't explain.** Especially `terraform apply`, `terraform destroy`, and anything touching IAM. Show the command and explain it; we run it.

## AWS rules

- Account uses AWS's new experience (Builder ID sign-in, no IAM users). Home Region is **eu-north-1** (Stockholm); everything goes there.
- Free plan with credits. Never create anything that bills by the hour without saying so first (NAT gateways, load balancers, RDS, public IPv4 addresses).
- Never use or ask for root credentials or long-term access keys. Local CLI access is via `aws login`.
- Every resource is created through Terraform in `infra/` (from Day 3 on), tagged `project = "job-market-radar"` and `owner = "<name>"`.

## Repo layout

```
api/          FastAPI service (shared). Tests in api/tests/
ai/           Fetcher, cleaning, LLM extraction, evaluation (ai/eval/). Tests: ai/test_*.py
dashboard/    Streamlit app (Day 6)
infra/        Terraform (Day 3 on)
docs/         contract.md — the shared interface
.github/      CI workflow
```

## Commands

```bash
# Local stack (Postgres + API; add --profile ai for the fetcher)
docker compose up --build
docker compose --profile ai up --build

# Lint (CI runs this on the whole repo)
ruff check .
ruff check --fix .

# Tests
cd api && python -m pytest
cd ai && python -m pytest
```

## Conventions

- **Never commit to `main` directly.** Branch, push, open a PR. CI (`test`, `test-ai`, `build`) must pass and the other person approves.
- **Branch names:** `cloud/<topic>`, `ai/<topic>`, `chore/<topic>`.
- **Run `ruff check --fix .` before pushing.** CI lints everything, including `ai/`.
- **Files are UTF-8 without BOM, LF line endings.** On Windows, don't create files with PowerShell's `>`; it writes UTF-16.
- **Secrets live in `.env` (gitignored) locally and in AWS Secrets Manager in the cloud.** Never commit `.env`, keys, `.pem` files or Terraform state.
- **If you change a table or an endpoint, update `docs/contract.md` in the same PR.**
