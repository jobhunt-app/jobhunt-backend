# Backlog

Generated from `scripts/github_setup.py`. The live board is the GitHub Project.

## M0 · Foundations

_Monorepo, tooling, FastAPI skeleton, Postgres + pgvector, CI basics._

- **Scaffold the backend repo layout** · type:chore, area:infra  
  Create the folder structure from CLAUDE.md so every later ticket has a home.
- **Backend tooling: uv, ruff, mypy --strict, pytest, pre-commit** · type:chore, area:backend  
  One-command quality checks for both Python packages.
- **FastAPI skeleton with /health and typed settings** · type:feature, area:backend  
  A running async API with configuration from the environment.
- **docker-compose with Postgres 16 + pgvector** · type:infra, area:infra  
  Local database identical to production's engine.
- **GitHub Actions: lint, type-check and test on every PR** · type:ci, area:infra  
  Public CI badge and fast feedback on PRs (Azure DevOps comes in M9).
- **Repo hygiene: PR template, issue templates, CONTRIBUTING** · type:docs  
  Make the repo look and work like a team project.

## M1 · Data model & tracker UI

_Postgres schema, legacy import, jobs table, job page, tracker kanban, profiles._

- **Database schema and Alembic migrations** · type:feature, area:backend  
  Async SQLAlchemy models for the core domain.
- **Import legacy data from the job-hunt script** · type:feature, area:backend  
  Bring existing jobs, statuses, notes, CVs and letters into Postgres.
- **Jobs list API with filters, sorting and pagination** · type:feature, area:backend  
  The main read endpoint for the jobs table.
- **Application status and notes API with history** · type:feature, area:backend  
  Replace the browser-only marks with persistent tracking.
- **Jobs table UI** · type:feature, area:frontend  
  Parity with the old jobs.html page, backed by the API.
- **Job detail page** · type:feature, area:frontend  
  Everything about one job in one place.
- **Tracker kanban board** · type:feature, area:frontend  
  See the pipeline at a glance.
- **Profiles: switch profile and isolate data** · type:feature, area:backend, area:frontend  
  Support a second user (e.g. business development) with their own settings and CV.
- **API tests for jobs and applications** · type:test, area:backend  
  Lock in M1 behaviour.

## M2 · Async scraper

_Async source adapters with rate limiting, dedupe, location rules, live progress._

- **Source adapter interface, RawJob model, rate limiter** · type:feature, area:scraper  
  A common contract every source implements.
- **ATS adapters: Greenhouse, Lever, Ashby, SmartRecruiters** · type:feature, area:scraper  
  Direct-from-employer sources (no paywalls).
- **Board adapters: Himalayas, Jobicy, Remotive, HN Who's Hiring** · type:feature, area:scraper  
  Remote job boards that link to employers.
- **LinkedIn public job search adapter** · type:feature, area:scraper  
  The biggest source for Yerevan and UAE jobs, scraped politely.
- **staff.am adapter** · type:feature, area:scraper  
  Armenia's main job board.
- **Telegram public channel adapter with source vetting** · type:feature, area:scraper  
  Recruiter posts from public channels.
- **Normalisation, dedupe, keyword pre-filter, location rules** · type:feature, area:scraper  
  Port the filtering logic that decides what's relevant.
- **Scrape endpoint with live progress (SSE)** · type:feature, area:backend, area:frontend  
  Start a scrape from the UI and watch it work.
- **Recorded fixtures for every source** · type:test, area:scraper  
  Tests never hit the network.

## M3 · gRPC scraper service

_Scraper as its own grpc.aio service streaming jobs to the API._

- **scraper.proto and code generation** · type:feature, area:scraper  
  Define the streaming contract between API and scraper.
- **grpc.aio scraper server with server-streaming RunScrape** · type:feature, area:scraper  
  The scraper runs as its own service.
- **API gRPC client bridge to DB and SSE** · type:feature, area:backend  
  The API consumes the stream, persists jobs and relays progress.
- **Cancellation, deadlines and health checks** · type:feature, area:scraper  
  Production-grade streaming behaviour.
- **In-process gRPC tests** · type:test, area:scraper  
  Test the contract without containers.
- **ADR-001: gRPC vs a task queue for the scraper** · type:docs  
  Record why the scraper is a streaming service.

## M4 · LLM job analysis

_Azure OpenAI structured outputs: requirements, eligibility, US hours, red flags._

- **LLM provider interface + Azure OpenAI client** · type:feature, area:llm  
  One place for all model access.
- **JobAnalysis schema and structured-output prompt** · type:feature, area:llm  
  Extract what matters from each posting.
- **Analysis pipeline with pre-filter, batching, caching and budget** · type:feature, area:llm, area:backend  
  Analyse only what's worth analysing, cheaply.
- **Show analysis on the job page** · type:feature, area:frontend  
  Make the AI's reasoning visible and checkable.
- **Use analysis in the eligibility filter** · type:feature, area:backend  
  'Open to me' becomes LLM-backed.
- **ADR-002: structured outputs vs regex heuristics** · type:docs  
  Record the trade-off.

## M5 · Embeddings & matching

_pgvector embeddings, fit score with explanations, semantic search._

- **Embeddings for jobs and CV bullets in pgvector** · type:feature, area:rag  
  Vectorise jobs and every master-CV bullet.
- **Fit score with explanation** · type:feature, area:rag  
  Rank jobs by how well they fit, and say why.
- **Fit UI: sort by fit, 'why it matches', similar jobs** · type:feature, area:frontend  
  Surface the matching in the product.
- **Semantic job search endpoint** · type:feature, area:rag, area:backend  
  Search by meaning, not keywords.

## M6 · Assistant, tailoring & letters

_Tool-calling assistant, honest CV tailoring with validator, streamed cover letters._

- **Master CV model and editor** · type:feature, area:frontend, area:backend  
  The CV as structured, editable data.
- **PDF rendering in the original design** · type:feature, area:backend  
  Port cv/build_cv.py to the API.
- **Tool registry and tool-calling loop** · type:feature, area:llm  
  The assistant's engine.
- **Tailored CV generation** · type:feature, area:llm  
  Tailor the CV to a job using retrieved bullets.
- **Tailoring validator (no invented experience)** · type:feature, area:llm  
  The honesty guarantee, enforced in code.
- **Cover letter generation with streaming** · type:feature, area:llm, area:frontend  
  Letters that follow the house style.
- **Assistant chat UI with tool events** · type:feature, area:frontend  
  Chat that shows what the assistant is doing.
- **Validator tests with injected violations** · type:test, area:llm  
  Prove the guarantee.

## M7 · Observability & evals

_Langfuse traces and prompts, golden-set evals, OpenTelemetry → Azure Monitor._

- **Langfuse traces and prompt management** · type:feature, area:obs  
  See every LLM call and its cost.
- **Job-analysis golden set and eval runner** · type:test, area:llm  
  Measure analysis accuracy.
- **Tailoring honesty eval** · type:test, area:llm  
  Measure tailoring quality and honesty.
- **OpenTelemetry → Azure Monitor** · type:feature, area:obs  
  Service-level telemetry.
- **Run evals in CI when prompts change** · type:ci, area:llm  
  Catch regressions before merge.

## M8 · Voice mock interview

_ASR → LLM → TTS streaming interview with latency tracking._

- **Browser mic capture and WebSocket streaming** · type:feature, area:voice, area:frontend  
  Stream the candidate's voice to the API.
- **Azure Speech streaming ASR** · type:feature, area:voice  
  Live transcription.
- **Interviewer persona from job + CV** · type:feature, area:voice, area:llm  
  Questions grounded in the actual job.
- **Sentence chunker + streaming TTS + playback** · type:feature, area:voice  
  Speak before the full answer is generated.
- **Barge-in cancellation** · type:feature, area:voice  
  Interrupt the interviewer naturally.
- **Latency instrumentation and panel** · type:feature, area:voice, area:obs  
  Measure and show the voice chain.
- **Interview feedback report** · type:feature, area:voice, area:llm  
  Actionable feedback after the session.

## M9 · Containers & Azure

_Docker, Azure DevOps pipelines, Container Apps, scheduled scrape, monitoring._

- **Dockerfiles for api, scraper and frontend** · type:infra, area:infra  
  Small, secure images.
- **Full-stack docker-compose** · type:infra, area:infra  
  One command runs everything locally.
- **Azure DevOps pipeline: lint, test, build, push to ACR** · type:ci, area:infra  
  The CI/CD tool the target team uses.
- **Deploy to Azure Container Apps** · type:infra, area:infra  
  Run in the cloud.
- **Scheduled daily scrape** · type:infra, area:scraper  
  The feed refreshes itself.
- **Dashboards, alerts and budget** · type:infra, area:obs  
  Operate it like production.

## M10 · Stretch

_Multi-LLM routing, Kubernetes, inbox sync, load testing._

- **Multi-LLM router** · type:feature, area:llm  
  Right model for each job, with fallback.
- **Kubernetes manifests / Helm for AKS** · type:infra, area:infra  
  Practise the migration path.
- **Gmail inbox sync** · type:feature, area:llm, area:backend  
  Keep the tracker up to date from email.
- **Load test with k6** · type:test, area:infra  
  Know the limits.
