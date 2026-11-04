# JobHunt App

A full-stack rebuild of Tigran's personal job-search tool. It scrapes job boards and company career pages, scores jobs against his profile, tracks applications, and uses an LLM to tailor CVs and cover letters, plus a voice mock-interview mode.

The original works today as a Python script plus a static HTML page in `~/Documents/job-hunt/`. Use it as the **reference implementation** for sources, filters and CV rendering (`jobhunt.py`, `profile.json`, `cv/master.json`, `cv/build_cv.py`, `template.html`, and the rules in its `CLAUDE.md`). **Don't modify that folder**: it's in daily use. Read from it, port its logic here.

The owner (Tigran) is building this **himself, with Claude Code as a pair**, to learn the stack of an upcoming work project (from February 2027). **Learning beats speed.** Explain non-obvious decisions briefly, let him make the design calls, and don't generate a whole milestone in one go.

Full brief and milestones: `docs/PROJECT_PLAN.md`. Architecture: `docs/architecture.md`. **Read both before starting work.**

## Stack (deliberately mirrors the target work project, keep it that way)

- **Backend:** Python 3.12, FastAPI (async everywhere), Pydantic v2, `uv`. HTTP scraping with `httpx.AsyncClient`.
- **Database:** PostgreSQL 16 + `pgvector`, SQLAlchemy 2 (async) + Alembic.
- **LLM:** Azure OpenAI via the official `openai` SDK (`AsyncAzureOpenAI`): streaming, **tool calling**, **structured outputs** (JSON schema from Pydantic), embeddings (`text-embedding-3-small`). All LLM access goes through `app/llm/` behind a provider interface (multi-LLM comes later).
- **Service-to-service streaming:** gRPC (`grpcio`, `grpc.aio`, protos in `proto/`). The scraper runs as its own service and streams results to the API.
- **Speech (voice mock interview):** Azure AI Speech (`azure-cognitiveservices-speech`) streaming ASR and TTS, behind `app/speech/`.
- **Observability:** Langfuse (LLM traces, prompt management, evals) + OpenTelemetry → Azure Monitor / Application Insights (`azure-monitor-opentelemetry`).
- **Frontend:** React + TypeScript + Vite, TanStack Query (+ TanStack Table for the job list), React Router. Server-Sent Events or WebSocket for live updates.
- **PDF rendering:** port `cv/build_cv.py` (HTML → PDF via headless Chromium; Playwright inside the container).
- **Containers & CI/CD:** Docker (multi-stage), docker-compose for local; Azure DevOps Pipelines (YAML) → Azure Container Registry → Azure Container Apps.
- **Tests:** pytest + pytest-asyncio, httpx `AsyncClient`, `respx` for mocking job-board HTTP (recorded fixtures, no live scraping in tests); LLM mocked in unit tests; a golden eval set for LLM behaviour. Frontend: Vitest + React Testing Library.

## Repo layout (target)

```
backend/
  api/                FastAPI app (the gateway the browser talks to)
    app/
      api/            routers: jobs, applications, profile, cv, letters, assistant, interview, scrape
      db/             models, session, alembic migrations
      llm/            provider interface, prompts/, tools/, structured-output schemas
      rag/            embeddings, retrieval, matching
      cv/             CV model, tailoring rules + validation, PDF rendering
      speech/         ASR/TTS interfaces (mock interview)
      telemetry.py
    tests/
  scraper/            gRPC scraper service: one async adapter per source
    sources/          linkedin.py, staffam.py, greenhouse.py, ashby.py, lever.py, himalayas.py, telegram.py, …
    tests/fixtures/   recorded HTML/JSON responses
proto/                scraper.proto (and interview.proto if used)
frontend/
evals/                golden sets + runners (job analysis, tailoring honesty)
scripts/              one-off tools, e.g. import from ~/Documents/job-hunt
infra/                docker-compose.yml, azure-pipelines/*.yml, (stretch) k8s/
docs/                 plan, architecture, adr/
```

## Domain rules (carried over from the working tool, they matter)

- **Never use pay-to-apply sources:** no RemoteOK, no aggregators that paywall "apply" (up2staff, Working Nomads, wantapply, remoteworldwide, codingjobboard), no Telegram channels that only repost those. Prefer sources that link to the employer's own page or ATS.
- **Be polite to sources.** LinkedIn's public job search (no login) gets ~4 s between requests and backs off on 429. Never scrape behind a login. Don't try to get around bot protection (Bayt, GulfTalent, Indeed and Glassdoor block automation, so leave them out).
- **Location eligibility** is the core filter: remote and open to Armenia, Yerevan, or the UAE (the user would relocate). Board metadata lies sometimes ("Worldwide" while the description says US-only), so the description wins.
- **CV tailoring may only reorder, rephrase and trim** what's in the master CV. **Never invent** skills, tools, projects, numbers, dates, titles or companies; never drop a whole job. This must be enforced in code (validation against the master CV), not just in the prompt.
- **Cover letters:** 200–260 words, direct, concrete facts from the CV, and gaps stated honestly in one sentence.
- Multi-profile from the start: Tigran's profile (software, AI) and his wife's (business development) use the same app with different `profile` settings.

## Conventions

- **Async all the way.** No blocking calls in handlers; wrap unavoidable sync SDK calls in `asyncio.to_thread`.
- Config via `pydantic-settings`; `.env.example` lists every variable; **never commit secrets**.
- Full type hints; `mypy --strict` on backend packages. Pydantic models for every request, response and LLM structured output.
- `ruff check` + `ruff format`; frontend ESLint + Prettier, strict TypeScript.
- Prompts live in `app/llm/prompts/*.md` or Langfuse prompt management, never as scattered inline strings.
- **Every LLM call is traced** in Langfuse (latency, tokens, cost); tool calls validated through Pydantic before execution.
- Tests with every feature; scrapers are tested against recorded fixtures.
- Small commits, conventional messages (`feat:`, `fix:`, `test:`, `docs:`), one milestone per branch, merged by PR with a self-review checklist.
- Notable decisions → short ADRs in `docs/adr/NNN-title.md`.
- **Don't commit or push unless Tigran asks.**

## Commands (fill in as they come to exist)

```bash
cd backend/api && uv sync && uv run uvicorn app.main:app --reload
uv run pytest && uv run ruff check . && uv run mypy app
cd frontend && npm install && npm run dev && npm test
docker compose -f infra/docker-compose.yml up --build
```

## How to work with Tigran

- **One milestone at a time**, in the order of `docs/PROJECT_PLAN.md`. At the start of a milestone, restate its acceptance criteria and propose a short task list; wait for his OK.
- Show how things work (a small example, a test) before writing large amounts of code he hasn't read.
- At the end of a milestone, check every acceptance criterion and update the Status table in `docs/PROJECT_PLAN.md`.
- Azure costs money: before creating any Azure resource, say what it is and roughly what it costs, prefer free tiers, and keep a teardown command.
