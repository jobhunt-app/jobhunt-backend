# JobHunt App

A full-stack job-search assistant: an async scraper streams jobs from company career pages and job boards, an LLM analyses each posting (requirements, location eligibility, red flags) and scores it against your CV with embeddings, and an assistant with tool calling tailors your CV and cover letter without ever inventing experience. Plus a voice mock interview (ASR → LLM → TTS).

**Stack:** Python · FastAPI (async) · Azure OpenAI (tool calling, structured outputs, embeddings) · Postgres + pgvector · gRPC streaming · Azure AI Speech · React + TypeScript · Langfuse · Azure Monitor · Docker · Azure DevOps

- Plan and milestones: [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md)
- Business case & requirements: [docs/BUSINESS.md](docs/BUSINESS.md)
- Architecture: [docs/architecture.md](docs/architecture.md)
- Backlog: [docs/BACKLOG.md](docs/BACKLOG.md) (live board: GitHub Project "JobHunt App")

_Work in progress. See the Status table in the plan._
