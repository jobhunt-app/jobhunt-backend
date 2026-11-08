# Contributing

## Workflow

1. Every change starts from a **GitHub issue** (use the Feature or Bug template).
2. Branch from `main`, **one branch per issue**:

   ```
   <type>/<issue#>-<short-slug>
   feat/3-fastapi-health
   chore/2-backend-tooling
   ```

3. Open a PR into `main`. The template's self-review checklist must be ticked and the body must contain `Closes #<issue#>`.
4. `main` is protected: changes only through PRs, no force pushes, and the CI checks (`checks`, `test-api`, `test-scraper`) must pass before merging.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/), small and focused, with an optional scope:

```
feat(api): report database connectivity in /health
fix(scraper): back off on 429 from LinkedIn
chore(tooling): pin setup-uv
docs: add ADR for pgvector
```

Types: `feat`, `fix`, `test`, `docs`, `chore`, `ci`, `refactor`.

## Setup

Requirements: [uv](https://docs.astral.sh/uv/), Docker Desktop.

```bash
uv sync                                          # one .venv for the whole workspace
uv tool install pre-commit && pre-commit install # hooks run on every commit
cp backend/api/.env.example backend/api/.env     # then adjust values if needed
```

## Running things

```bash
docker compose -f infra/docker-compose.yml up db   # Postgres 16 + pgvector on localhost:5432

cd backend/api && uv run uvicorn app.main:app --reload   # API on http://localhost:8000 (docs at /docs)
```

## Checks

```bash
pre-commit run --all-files                         # everything CI's `checks` job runs
cd backend/api && uv run pytest                    # needs the db container running
cd backend/scraper && uv run pytest
```

## Notable decisions

Write a short ADR in `docs/adr/NNN-title.md`: context, decision, consequences.
