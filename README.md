# JobHunt App

[![CI](https://github.com/jobhunt-app/jobhunt-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/jobhunt-app/jobhunt-backend/actions/workflows/ci.yml)

A full-stack job-search assistant: an async scraper streams jobs from company career pages and job boards, an LLM analyses each posting (requirements, location eligibility, red flags) and scores it against your CV with embeddings, and an assistant with tool calling tailors your CV and cover letter without ever inventing experience. Plus a voice mock interview (ASR → LLM → TTS).

**Stack:** Python · FastAPI (async) · Azure OpenAI (tool calling, structured outputs, embeddings) · Postgres + pgvector · gRPC streaming · Azure AI Speech · Langfuse · Azure Monitor · Docker · Azure DevOps

- Plan and milestones: [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md)
- Business case & requirements: [docs/BUSINESS.md](docs/BUSINESS.md)
- Architecture: [docs/architecture.md](docs/architecture.md)
- Backlog: [docs/BACKLOG.md](docs/BACKLOG.md) · tickets: [GitHub Issues](https://github.com/jobhunt-app/jobhunt-backend/issues) grouped by [milestone](https://github.com/jobhunt-app/jobhunt-backend/milestones) · [project board](https://github.com/users/tiiikk/projects/1)

This repo is the **backend** (API + scraper). The React web app and a React Native mobile app live in separate repos (coming later).

Built by me with [Claude Code](https://claude.com/claude-code) as a pair-programming partner: I make the design decisions and write the core code, Claude helps with boilerplate, explanations and reviews. That's why commits carry a `Co-Authored-By: Claude` line.

_Work in progress. See the Status table in the plan._
