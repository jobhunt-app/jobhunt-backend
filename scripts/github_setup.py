#!/usr/bin/env python3
"""
Creates the GitHub side of the project from the backlog below:
labels, milestones, issues, and a GitHub Project board with every issue on it.

  python3 scripts/github_setup.py --export-md     # write docs/BACKLOG.md (no network)
  python3 scripts/github_setup.py --dry-run       # print what would be created
  python3 scripts/github_setup.py --repo OWNER/NAME   # create everything (needs `gh auth login -s project`)
  python3 scripts/github_setup.py --repo OWNER/NAME --no-project   # labels, milestones, issues only

Safe to re-run: existing labels, milestones and issues (same title) are skipped.
Only uses the Python standard library and the `gh` CLI.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

LABELS = [
    ("type:feature", "1d76db", "New user-facing or API capability"),
    ("type:chore", "c5def5", "Setup, tooling, refactoring"),
    ("type:infra", "5319e7", "Containers, cloud, deployment"),
    ("type:ci", "0e8a16", "Pipelines and automation"),
    ("type:test", "fbca04", "Tests and evals"),
    ("type:docs", "0075ca", "Documentation and ADRs"),
    ("area:backend", "bfdadc", "FastAPI API service"),
    ("area:frontend", "bfd4f2", "React app"),
    ("area:scraper", "d4c5f9", "Scraper service and source adapters"),
    ("area:llm", "f9d0c4", "LLM integration, prompts, tools"),
    ("area:rag", "fef2c0", "Embeddings, pgvector, retrieval"),
    ("area:voice", "c2e0c6", "ASR → LLM → TTS mock interview"),
    ("area:obs", "e4e669", "Langfuse, OpenTelemetry, Azure Monitor"),
    ("area:infra", "d93f0b", "Docker, Azure, CI/CD"),
    ("priority:high", "b60205", "Do first within the milestone"),
    ("priority:medium", "fbca04", "Normal priority"),
    ("priority:low", "0e8a16", "Nice to have"),
]

MILESTONES = [
    ("M0 · Foundations", "Monorepo, tooling, FastAPI skeleton, Postgres + pgvector, CI basics."),
    ("M1 · Data model & tracker UI", "Postgres schema, legacy import, jobs table, job page, tracker kanban, profiles."),
    ("M2 · Async scraper", "Async source adapters with rate limiting, dedupe, location rules, live progress."),
    ("M3 · gRPC scraper service", "Scraper as its own grpc.aio service streaming jobs to the API."),
    ("M4 · LLM job analysis", "Azure OpenAI structured outputs: requirements, eligibility, US hours, red flags."),
    ("M5 · Embeddings & matching", "pgvector embeddings, fit score with explanations, semantic search."),
    ("M6 · Assistant, tailoring & letters", "Tool-calling assistant, honest CV tailoring with validator, streamed cover letters."),
    ("M7 · Observability & evals", "Langfuse traces and prompts, golden-set evals, OpenTelemetry → Azure Monitor."),
    ("M8 · Voice mock interview", "ASR → LLM → TTS streaming interview with latency tracking."),
    ("M9 · Containers & Azure", "Docker, Azure DevOps pipelines, Container Apps, scheduled scrape, monitoring."),
    ("M10 · Stretch", "Multi-LLM routing, Kubernetes, inbox sync, load testing."),
]

# (milestone index, title, labels, goal, acceptance criteria)
ISSUES = [
    # ── M0 ─────────────────────────────────────────────────────────────
    (0, "Scaffold the backend repo layout", ["type:chore", "area:infra", "priority:high"],
     "Create the folder structure from CLAUDE.md so every later ticket has a home.",
     ["`backend/api`, `backend/scraper`, `proto`, `evals`, `scripts`, `infra`, `docs/adr` exist",
      "Root README links to the plan, business doc and architecture",
      "`.gitignore` covers Python, Node, `.env`, local data"]),
    (0, "Backend tooling: uv, ruff, mypy --strict, pytest, pre-commit", ["type:chore", "area:backend", "priority:high"],
     "One-command quality checks for both Python packages.",
     ["`uv sync` installs deps for api and scraper", "`ruff check`, `ruff format --check`, `mypy --strict` pass",
      "`pytest` runs with pytest-asyncio", "pre-commit runs ruff and mypy on commit"]),
    (0, "FastAPI skeleton with /health and typed settings", ["type:feature", "area:backend", "priority:high"],
     "A running async API with configuration from the environment.",
     ["`GET /health` returns status, version and DB connectivity", "Settings via `pydantic-settings`; `.env.example` documents every variable",
      "Structured JSON logging", "Test for `/health` using httpx `AsyncClient`"]),
    (0, "docker-compose with Postgres 16 + pgvector", ["type:infra", "area:infra", "priority:high"],
     "Local database identical to production's engine.",
     ["`docker compose up db` starts Postgres with the `vector` extension available", "Named volume for data; healthcheck", "Connection string in `.env.example`"]),
    (0, "GitHub Actions: lint, type-check and test on every PR", ["type:ci", "area:infra", "priority:medium"],
     "Public CI badge and fast feedback on PRs (Azure DevOps comes in M9).",
     ["Workflow runs ruff, mypy and pytest for api and scraper", "Runs on PRs and pushes to `main`", "Status badge in README"]),
    (0, "Repo hygiene: PR template, issue templates, CONTRIBUTING", ["type:docs", "priority:low"],
     "Make the repo look and work like a team project.",
     ["PR template with a self-review checklist (tests, types, docs, screenshots)", "Issue templates: feature, bug",
      "CONTRIBUTING.md: branch naming, conventional commits, how to run everything"]),

    # ── M1 ─────────────────────────────────────────────────────────────
    (1, "Database schema and Alembic migrations", ["type:feature", "area:backend", "priority:high"],
     "Async SQLAlchemy models for the core domain.",
     ["Tables: profiles, jobs, applications, status_history, cvs, cover_letters (see docs/architecture.md)",
      "Alembic migration creates them and enables `vector`", "Unique job URL; indexes for filters", "Model tests against a test database"]),
    (1, "Import legacy data from the job-hunt script", ["type:feature", "area:backend", "priority:high"],
     "Bring existing jobs, statuses, notes, CVs and letters into Postgres.",
     ["`scripts/import_legacy.py --from ~/Documents/job-hunt` imports profile.json, jobs.csv, cv/master.json, cv/tailored/*.json, cover_letters/*.md",
      "Idempotent (re-running doesn't duplicate)", "Personal data is never written into the repo", "Summary printed: counts per table"]),
    (1, "Jobs list API with filters, sorting and pagination", ["type:feature", "area:backend", "priority:high"],
     "The main read endpoint for the jobs table.",
     ["`GET /jobs` filters: text, location bucket, source, status, open-to-me, AI role", "Sort by score or date; cursor pagination",
      "Response models in Pydantic; p95 < 300 ms on 5k jobs"]),
    (1, "Application status and notes API with history", ["type:feature", "area:backend", "priority:high"],
     "Replace the browser-only marks with persistent tracking.",
     ["`PATCH /jobs/{id}/application` updates status and notes", "Every change writes `status_history` (from, to, at, source)",
      "Statuses: new, saved, applied, interview, rejected, irrelevant, expired"]),
    (1, "Jobs table UI", ["type:feature", "area:frontend", "priority:high"],
     "Parity with the old jobs.html page, backed by the API.",
     ["TanStack Table with search and filter controls", "Tags for location bucket, AI role, status, US hours",
      "Status buttons (applied / not relevant / expired) update optimistically", "Works on a 375 px wide screen"]),
    (1, "Job detail page", ["type:feature", "area:frontend", "priority:medium"],
     "Everything about one job in one place.",
     ["Description, source link, status, notes editor, history timeline", "Links to tailored CV and cover letter when they exist"]),
    (1, "Tracker kanban board", ["type:feature", "area:frontend", "priority:medium"],
     "See the pipeline at a glance.",
     ["Columns per status; drag a card to change status", "Counts per column", "Filter by profile"]),
    (1, "Profiles: switch profile and isolate data", ["type:feature", "area:backend", "area:frontend", "priority:medium"],
     "Support a second user (e.g. business development) with their own settings and CV.",
     ["Profile switcher in the UI", "Jobs, applications and CVs are scoped by profile", "Profile settings editable (keywords, sources, relocate)"]),
    (1, "API tests for jobs and applications", ["type:test", "area:backend", "priority:medium"],
     "Lock in M1 behaviour.",
     ["Tests for filters, pagination, status updates and history", "Test database per test session"]),

    # ── M2 ─────────────────────────────────────────────────────────────
    (2, "Source adapter interface, RawJob model, rate limiter", ["type:feature", "area:scraper", "priority:high"],
     "A common contract every source implements.",
     ["`async def fetch(profile) -> AsyncIterator[RawJob]`", "Shared `httpx.AsyncClient` with per-source rate limits, retries and back-off on 429",
      "One failing source never fails the run"]),
    (2, "ATS adapters: Greenhouse, Lever, Ashby, SmartRecruiters", ["type:feature", "area:scraper", "priority:high"],
     "Direct-from-employer sources (no paywalls).",
     ["Company slugs from the profile", "Location, remote flag and description normalised", "Fixture tests per adapter"]),
    (2, "Board adapters: Himalayas, Jobicy, Remotive, HN Who's Hiring", ["type:feature", "area:scraper", "priority:medium"],
     "Remote job boards that link to employers.",
     ["Ported from jobhunt.py", "RemoteOK and pay-to-apply aggregators are explicitly excluded (documented)", "Fixture tests"]),
    (2, "LinkedIn public job search adapter", ["type:feature", "area:scraper", "priority:high"],
     "The biggest source for Yerevan and UAE jobs, scraped politely.",
     ["Public guest endpoint only, never logged in", "geoIds for Armenia and relocation places; OR-combined keywords",
      "≥ 4 s between requests; back-off and partial results on 429", "Fixture tests"]),
    (2, "staff.am adapter", ["type:feature", "area:scraper", "priority:medium"],
     "Armenia's main job board.",
     ["Parses `__NEXT_DATA__`; handles per-language slugs", "Categories from profile", "Fixture tests"]),
    (2, "Telegram public channel adapter with source vetting", ["type:feature", "area:scraper", "priority:low"],
     "Recruiter posts from public channels.",
     ["Reads `t.me/s/<channel>`; skips résumé posts", "Extracts title/company from structured posts",
      "Documented vetting rule: channels must link to employers, not paywalled reposts"]),
    (2, "Normalisation, dedupe, keyword pre-filter, location rules", ["type:feature", "area:scraper", "priority:high"],
     "Port the filtering logic that decides what's relevant.",
     ["Dedupe by URL and company+title", "Role/exclude patterns and keyword score from profile",
      "Location buckets: Remote (open to Armenia), Yerevan, relocate places; long country lists summarised", "Unit tests with real examples"]),
    (2, "Scrape endpoint with live progress (SSE)", ["type:feature", "area:backend", "area:frontend", "priority:high"],
     "Start a scrape from the UI and watch it work.",
     ["`POST /scrape` starts a run; `GET /scrape/{id}/events` streams progress via SSE",
      "UI panel shows per-source counts and errors", "Offline or mostly-failed runs keep previous results"]),
    (2, "Recorded fixtures for every source", ["type:test", "area:scraper", "priority:medium"],
     "Tests never hit the network.",
     ["respx mocks with recorded responses per source", "A script to refresh fixtures manually"]),

    # ── M3 ─────────────────────────────────────────────────────────────
    (3, "scraper.proto and code generation", ["type:feature", "area:scraper", "priority:high"],
     "Define the streaming contract between API and scraper.",
     ["`proto/scraper.proto` as in docs/architecture.md", "Codegen script for both services; generated code typed"]),
    (3, "grpc.aio scraper server with server-streaming RunScrape", ["type:feature", "area:scraper", "priority:high"],
     "The scraper runs as its own service.",
     ["Streams Progress, RawJob, SourceError, Done events", "Sources run concurrently with their own rate limits"]),
    (3, "API gRPC client bridge to DB and SSE", ["type:feature", "area:backend", "priority:high"],
     "The API consumes the stream, persists jobs and relays progress.",
     ["Upserts jobs as they arrive", "Relays progress to the browser", "UI flow unchanged from M2"]),
    (3, "Cancellation, deadlines and health checks", ["type:feature", "area:scraper", "priority:medium"],
     "Production-grade streaming behaviour.",
     ["Cancel from the UI stops the server stream", "Per-call deadline", "gRPC health protocol implemented and used by compose"]),
    (3, "In-process gRPC tests", ["type:test", "area:scraper", "priority:medium"],
     "Test the contract without containers.",
     ["Tests start an in-process server and assert event order, errors and cancellation"]),
    (3, "ADR-001: gRPC vs a task queue for the scraper", ["type:docs", "priority:low"],
     "Record why the scraper is a streaming service.",
     ["Context, options (gRPC, Celery/Arq, plain HTTP), decision, consequences"]),

    # ── M4 ─────────────────────────────────────────────────────────────
    (4, "LLM provider interface + Azure OpenAI client", ["type:feature", "area:llm", "priority:high"],
     "One place for all model access.",
     ["`AsyncAzureOpenAI` wrapper: chat (stream), structured output, embeddings", "Provider interface ready for a second provider",
      "Retries, timeouts, token/cost accounting; every call traced in Langfuse"]),
    (4, "JobAnalysis schema and structured-output prompt", ["type:feature", "area:llm", "priority:high"],
     "Extract what matters from each posting.",
     ["Pydantic schema: required_skills, nice_to_have, seniority, employment_type, location_eligibility (with quoted evidence), us_hours, salary, red_flags",
      "Prompt versioned in Langfuse", "Handles 'Worldwide' labels contradicted by the description"]),
    (4, "Analysis pipeline with pre-filter, batching, caching and budget", ["type:feature", "area:llm", "area:backend", "priority:high"],
     "Analyse only what's worth analysing, cheaply.",
     ["Runs only on jobs passing the keyword pre-filter", "Cached by content hash; re-analysed only on prompt version change",
      "Daily token budget; cost per run logged"]),
    (4, "Show analysis on the job page", ["type:feature", "area:frontend", "priority:medium"],
     "Make the AI's reasoning visible and checkable.",
     ["Eligibility with the quoted sentence", "Red-flag and US-hours badges", "Required vs nice-to-have skills"]),
    (4, "Use analysis in the eligibility filter", ["type:feature", "area:backend", "priority:medium"],
     "'Open to me' becomes LLM-backed.",
     ["Filter combines analysis with the regex pre-filter", "Disagreements between the two are flagged for review"]),
    (4, "ADR-002: structured outputs vs regex heuristics", ["type:docs", "priority:low"],
     "Record the trade-off.",
     ["Accuracy vs cost vs latency, with eval numbers once M7 lands"]),

    # ── M5 ─────────────────────────────────────────────────────────────
    (5, "Embeddings for jobs and CV bullets in pgvector", ["type:feature", "area:rag", "priority:high"],
     "Vectorise jobs and every master-CV bullet.",
     ["`text-embedding-3-small`, 1536 dims, HNSW cosine index", "Embedded once per content hash", "Backfill command"]),
    (5, "Fit score with explanation", ["type:feature", "area:rag", "priority:high"],
     "Rank jobs by how well they fit, and say why.",
     ["Score = keyword + semantic similarity + analysis signals (eligibility, seniority)", "Top 3 matching CV bullets stored per job",
      "Weights configurable per profile"]),
    (5, "Fit UI: sort by fit, 'why it matches', similar jobs", ["type:feature", "area:frontend", "priority:medium"],
     "Surface the matching in the product.",
     ["Sort by fit in the table", "'Why it matches' section on the job page", "Similar jobs list"]),
    (5, "Semantic job search endpoint", ["type:feature", "area:rag", "area:backend", "priority:low"],
     "Search by meaning, not keywords.",
     ["`GET /jobs/search?q=` uses embeddings plus filters", "Used by the assistant's `search_jobs` tool in M6"]),

    # ── M6 ─────────────────────────────────────────────────────────────
    (6, "Master CV model and editor", ["type:feature", "area:frontend", "area:backend", "priority:high"],
     "The CV as structured, editable data.",
     ["CV JSON schema (contact, summary, skills, experience, projects, certificates, education)", "Editor UI with live preview"]),
    (6, "PDF rendering in the original design", ["type:feature", "area:backend", "priority:high"],
     "Port cv/build_cv.py to the API.",
     ["Playwright/Chromium renders HTML → PDF", "Same design as the original CV; links clickable", "Never overwrites a good PDF with a failed render"]),
    (6, "Tool registry and tool-calling loop", ["type:feature", "area:llm", "priority:high"],
     "The assistant's engine.",
     ["Tools defined from Pydantic models", "Parallel tool calls, step limit, timeouts", "Invalid arguments returned to the model as structured errors"]),
    (6, "Tailored CV generation", ["type:feature", "area:llm", "priority:high"],
     "Tailor the CV to a job using retrieved bullets.",
     ["Structured output in the CV schema", "Allowed: reorder, rephrase, trim, title focus", "A change summary for the user"]),
    (6, "Tailoring validator (no invented experience)", ["type:feature", "area:llm", "priority:high"],
     "The honesty guarantee, enforced in code.",
     ["Rules from docs/architecture.md (jobs, bullets, numbers, skills, certificates)", "Violations fed back to the model (max 2 retries), then shown to the user"]),
    (6, "Cover letter generation with streaming", ["type:feature", "area:llm", "area:frontend", "priority:medium"],
     "Letters that follow the house style.",
     ["200–260 words, concrete facts, gaps stated honestly", "Streams token by token; editable; saved per job"]),
    (6, "Assistant chat UI with tool events", ["type:feature", "area:frontend", "priority:medium"],
     "Chat that shows what the assistant is doing.",
     ["Streaming responses", "Tool calls rendered as compact events", "Actions (status change) require confirmation"]),
    (6, "Validator tests with injected violations", ["type:test", "area:llm", "priority:high"],
     "Prove the guarantee.",
     ["Tests inject a fake skill, a changed number, an invented bullet and a dropped job; all rejected"]),

    # ── M7 ─────────────────────────────────────────────────────────────
    (7, "Langfuse traces and prompt management", ["type:feature", "area:obs", "priority:high"],
     "See every LLM call and its cost.",
     ["One trace per assistant turn and per analysis batch", "Prompts pulled from Langfuse with version labels"]),
    (7, "Job-analysis golden set and eval runner", ["type:test", "area:llm", "priority:high"],
     "Measure analysis accuracy.",
     ["~40 labelled postings incl. known traps (false 'Worldwide', US hours, malicious listing)", "`evals/run_analysis.py` prints accuracy per field and stores a Langfuse dataset run"]),
    (7, "Tailoring honesty eval", ["type:test", "area:llm", "priority:high"],
     "Measure tailoring quality and honesty.",
     ["Validator pass rate + LLM-as-judge rubric (relevance, honesty, tone)", "Results table per prompt version"]),
    (7, "OpenTelemetry → Azure Monitor", ["type:feature", "area:obs", "priority:medium"],
     "Service-level telemetry.",
     ["`azure-monitor-opentelemetry` in API and scraper", "Custom metrics: scrape duration per source, LLM latency, errors"]),
    (7, "Run evals in CI when prompts change", ["type:ci", "area:llm", "priority:low"],
     "Catch regressions before merge.",
     ["CI job runs evals on PRs touching prompts; fails below a threshold"]),

    # ── M8 ─────────────────────────────────────────────────────────────
    (8, "Browser mic capture and WebSocket streaming", ["type:feature", "area:voice", "area:frontend", "priority:high"],
     "Stream the candidate's voice to the API.",
     ["AudioWorklet captures 16 kHz mono PCM16", "Push-to-talk; frames sent over WebSocket"]),
    (8, "Azure Speech streaming ASR", ["type:feature", "area:voice", "priority:high"],
     "Live transcription.",
     ["Push-stream recognition; partial and final transcripts back to the UI", "Language configurable (en, ru)"]),
    (8, "Interviewer persona from job + CV", ["type:feature", "area:voice", "area:llm", "priority:high"],
     "Questions grounded in the actual job.",
     ["Prompt built from job analysis and CV", "Asks follow-ups on weak answers; probes known gaps"]),
    (8, "Sentence chunker + streaming TTS + playback", ["type:feature", "area:voice", "priority:high"],
     "Speak before the full answer is generated.",
     ["LLM tokens chunked into sentences; each sentence sent to Azure TTS immediately", "Audio chunks streamed and played in order"]),
    (8, "Barge-in cancellation", ["type:feature", "area:voice", "priority:medium"],
     "Interrupt the interviewer naturally.",
     ["New speech stops playback and cancels generation and TTS"]),
    (8, "Latency instrumentation and panel", ["type:feature", "area:voice", "area:obs", "priority:medium"],
     "Measure and show the voice chain.",
     ["t0 final transcript, t1 first token, t2 first audio recorded and traced", "UI panel per turn; p50 time-to-first-audio tracked"]),
    (8, "Interview feedback report", ["type:feature", "area:voice", "area:llm", "priority:low"],
     "Actionable feedback after the session.",
     ["Strengths, weak answers, what to prepare; saved to the job's notes"]),

    # ── M9 ─────────────────────────────────────────────────────────────
    (9, "Dockerfiles for api, scraper and frontend", ["type:infra", "area:infra", "priority:high"],
     "Small, secure images.",
     ["Multi-stage, non-root, healthchecks", "Chromium for PDFs in the api image", "Frontend served by nginx"]),
    (9, "Full-stack docker-compose", ["type:infra", "area:infra", "priority:high"],
     "One command runs everything locally.",
     ["Frontend, api, scraper, Postgres, optional self-hosted Langfuse", "Fresh clone + `.env` + `docker compose up` works"]),
    (9, "Azure DevOps pipeline: lint, test, build, push to ACR", ["type:ci", "area:infra", "priority:high"],
     "The CI/CD tool the target team uses.",
     ["YAML pipeline with stages", "Images pushed to Azure Container Registry", "Secrets from a variable group or Key Vault"]),
    (9, "Deploy to Azure Container Apps", ["type:infra", "area:infra", "priority:high"],
     "Run in the cloud.",
     ["Staging environment deployed on merge to `main`", "Postgres (Flexible Server or container) with pgvector", "Teardown script"]),
    (9, "Scheduled daily scrape", ["type:infra", "area:scraper", "priority:medium"],
     "The feed refreshes itself.",
     ["Container Apps job runs the scrape daily", "Failures alert"]),
    (9, "Dashboards, alerts and budget", ["type:infra", "area:obs", "priority:medium"],
     "Operate it like production.",
     ["Application Insights dashboard", "Alerts: scrape failure, LLM error rate", "Azure budget alert; monthly cost documented"]),

    # ── M10 ────────────────────────────────────────────────────────────
    (10, "Multi-LLM router", ["type:feature", "area:llm", "priority:medium"],
     "Right model for each job, with fallback.",
     ["Second provider behind the interface", "Small/fast model for analysis, strong model for writing; fallback on errors",
      "Comparison report: cost, latency, eval scores"]),
    (10, "Kubernetes manifests / Helm for AKS", ["type:infra", "area:infra", "priority:low"],
     "Practise the migration path.",
     ["Deployments, services, HPA, config/secrets", "Runs on kind locally", "ADR: Container Apps vs AKS"]),
    (10, "Gmail inbox sync", ["type:feature", "area:llm", "area:backend", "priority:medium"],
     "Keep the tracker up to date from email.",
     ["Read-only Gmail access", "LLM classifies: confirmation, rejection, next step, red flag", "Suggests tracker updates; the user confirms"]),
    (10, "Load test with k6", ["type:test", "area:infra", "priority:low"],
     "Know the limits.",
     ["k6 script for main read endpoints", "p95 latency and error rate documented"]),
]


def body(goal, criteria, milestone):
    lines = [f"**Goal:** {goal}", "", "### Acceptance criteria"] + [f"- [ ] {c}" for c in criteria]
    lines += ["", f"_Milestone: {milestone}. See [project plan](../blob/main/docs/PROJECT_PLAN.md)._"]
    return "\n".join(lines)


def export_md():
    out = ["# Backlog", "", "Generated from `scripts/github_setup.py`. The live board is the GitHub Project.", ""]
    for i, (m, desc) in enumerate(MILESTONES):
        out += [f"## {m}", "", f"_{desc}_", ""]
        for (mi, title, labels, goal, crit) in ISSUES:
            if mi == i:
                out.append(f"- **{title}** · {', '.join(l for l in labels if l.startswith(('type:', 'area:')))}  \n  {goal}")
        out.append("")
    path = os.path.join(ROOT, "docs", "BACKLOG.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"wrote {os.path.relpath(path, ROOT)} ({len(ISSUES)} issues, {len(MILESTONES)} milestones)")


def gh(*args, check=True):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"gh {' '.join(args[:3])}… failed:\n{r.stderr}")
    return r.stdout.strip()


def setup(repo, dry, project=True):
    say = (lambda *a: print("  would", *a)) if dry else (lambda *a: print("  ", *a))
    owner = repo.split("/")[0]

    existing_labels = set() if dry else {l["name"] for l in json.loads(gh("label", "list", "-R", repo, "--limit", "200", "--json", "name"))}
    for name, color, desc in LABELS:
        if name in existing_labels:
            continue
        say("create label", name)
        if not dry:
            gh("label", "create", name, "-R", repo, "--color", color, "--description", desc, "--force")

    existing_ms = set() if dry else {m["title"] for m in json.loads(gh("api", f"repos/{repo}/milestones?state=all&per_page=100"))}
    for title, desc in MILESTONES:
        if title in existing_ms:
            continue
        say("create milestone", title)
        if not dry:
            gh("api", f"repos/{repo}/milestones", "-f", f"title={title}", "-f", f"description={desc}")

    project_number = None
    if not project:
        print("   (skipping the GitHub Project board)")
    elif not dry:
        projects = json.loads(gh("project", "list", "--owner", owner, "--format", "json"))["projects"]
        found = next((p for p in projects if p["title"] == "JobHunt App"), None)
        if found:
            project_number = found["number"]
        else:
            project_number = json.loads(gh("project", "create", "--owner", owner, "--title", "JobHunt App", "--format", "json"))["number"]
            gh("project", "link", str(project_number), "--owner", owner, "--repo", repo, check=False)
        print(f"   project #{project_number}")
    else:
        say("create project 'JobHunt App' and link it to the repo")

    existing_issues = set() if dry else {i["title"] for i in json.loads(gh("issue", "list", "-R", repo, "--state", "all", "--limit", "500", "--json", "title"))}
    for (mi, title, labels, goal, crit) in ISSUES:
        if title in existing_issues:
            continue
        milestone = MILESTONES[mi][0]
        say("create issue", f"[{milestone.split(' ·')[0]}] {title}")
        if dry:
            continue
        url = gh("issue", "create", "-R", repo, "--title", title, "--body", body(goal, crit, milestone),
                 "--milestone", milestone, *sum((["--label", l] for l in labels), []))
        if project_number is not None:
            gh("project", "item-add", str(project_number), "--owner", owner, "--url", url)
        time.sleep(1.2)  # stay well under GitHub's secondary rate limits for content creation
    print("done" if not dry else f"\n{len(LABELS)} labels, {len(MILESTONES)} milestones, {len(ISSUES)} issues")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", help="OWNER/NAME")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--export-md", action="store_true")
    ap.add_argument("--no-project", action="store_true", help="create labels, milestones and issues only, no Project board")
    a = ap.parse_args()
    if a.export_md:
        export_md()
    elif a.dry_run:
        setup(a.repo or "OWNER/REPO", dry=True, project=not a.no_project)
    elif a.repo:
        setup(a.repo, dry=False, project=not a.no_project)
    else:
        ap.print_help()
