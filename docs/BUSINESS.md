# JobHunt: product requirements & business case

| | |
|---|---|
| **Product** | JobHunt: an AI job-search copilot for experienced engineers and professionals searching remotely across borders |
| **Owner** | Tigran Manukyan |
| **Status** | Draft v1 · November 2026 |
| **Related** | [Project plan & milestones](PROJECT_PLAN.md) · [Architecture](architecture.md) |

---

## 1. Summary

Experienced professionals outside the US and EU (for example in Armenia, Georgia or Serbia) can work remotely for companies anywhere. But the job search is broken for them: listings are scattered across dozens of boards and career pages, "remote" often silently means "US only", many aggregators charge to apply or repost fake jobs, and every application needs a tailored CV and cover letter.

**JobHunt** finds the jobs a person can actually get, explains why each one fits, and prepares an honest, tailored application in minutes. It tracks every application through to the offer, and lets the candidate rehearse the interview by voice.

It started as a personal script that scanned ~6,000 listings a day across 30+ sources and produced 15+ tailored applications in a week. This document describes the product version.

## 2. Problem

| # | Problem | Evidence (from real use) |
|---|---|---|
| P1 | **Fragmentation.** Relevant jobs are spread across LinkedIn, local boards (staff.am), company ATS pages (Greenhouse, Lever, Ashby, SmartRecruiters), remote boards and Telegram channels. | Each source surfaced roles no other source had; LinkedIn alone had Yerevan-only roles missing elsewhere. |
| P2 | **False "remote".** Boards label jobs "Worldwide" while the description says US/Canada only, or requires US business hours. | e.g. a "Worldwide" applied-AI role whose description said "Remote – USA/Canada"; a "worldwide" role requiring 6pm–2am local hours. |
| P3 | **Pay-to-apply and scams.** Aggregators put paywalls in front of "apply"; some posts are fake or malicious. | A top-ranked repost led to a payment page; a job board later flagged a listing as malicious and told applicants not to run any code sent to them. |
| P4 | **Tailoring is slow and risky.** Tailoring a CV and letter per job takes 30–60 minutes; AI tools that do it tend to **invent experience**, which backfires in interviews. | Generic AI-written applications get filtered; invented skills get caught in screening. |
| P5 | **No memory.** Candidates lose track of where they applied, who rejected them, and which version of their CV went where. | Applying to the same role three times through a form led to instant automatic rejections. |
| P6 | **Interview prep is generic.** Practice questions aren't based on the actual job and the candidate's actual CV. | Interview gaps (RAG, evals, C++) were predictable from the job description but not rehearsed. |

## 3. Target users

**Primary persona: "Remote senior, outside the US"**
- 4–10 years of experience, software or adjacent (product, business development).
- Lives in a country with few local senior roles; open to remote work and sometimes relocation (e.g. UAE).
- Applies to 10–30 jobs a week; fluent in English, often bilingual (Russian, German…).
- Pain: time, false-remote listings, honest tailoring, tracking.

**Secondary persona: "The partner's search"**
- A non-engineer (e.g. business development) using the same tool with different searches, keywords and CV.
- Needs the same workflow without touching code.

**Out of scope for v1:** recruiters and companies (no employer side), students and entry-level searches, US-based candidates (the main value is eligibility filtering for non-US candidates).

## 4. Value proposition

> **Find only the jobs you can actually get, know why they fit, and send an honest, tailored application in five minutes.**

| Instead of… | JobHunt gives you… |
|---|---|
| 15 tabs of job boards | One feed from 30+ sources, deduplicated, refreshed daily |
| Guessing whether "remote" includes you | LLM-checked eligibility per job (country, hours, relocation), with the evidence quoted |
| Paywalls and scams | Sources vetted for direct-to-employer applying; red-flag detection |
| 45 minutes per application | A tailored CV + cover letter in minutes, **guaranteed not to invent experience** |
| Spreadsheets and memory | A tracker with history, auto-updated from your inbox (stretch) |
| Generic interview prep | A voice mock interview built from *that* job and *your* CV |

## 5. Competitive landscape

| Category | Examples | Gap JobHunt fills |
|---|---|---|
| Job boards / aggregators | LinkedIn, Himalayas, We Work Remotely, RemoteOK | No eligibility check for non-US candidates; some charge job-seekers; no tailoring |
| Auto-apply bots | Various "AI job copilots" | Mass-applying gets filtered and gets accounts banned; often invent or embellish experience |
| CV builders / AI writers | Resume builders, generic chat assistants | Not connected to real job feeds; no honesty guarantee; no tracking |
| Trackers | Spreadsheets, Notion templates, Huntr-style boards | Manual entry; no discovery or AI |

**Differentiators:** (1) eligibility-first filtering for non-US remote candidates; (2) an **honesty guarantee** enforced by code, not by prompt; (3) a vetted-source policy (no pay-to-apply); (4) one workflow from discovery to interview practice.

## 6. Product scope

### 6.1 Features (MoSCoW)

| Feature | Priority | Milestone |
|---|---|---|
| Multi-source scraping with live progress | Must | M2–M3 |
| Dedupe, keyword pre-filter, location rules | Must | M2 |
| LLM job analysis: requirements, seniority, eligibility, US hours, red flags | Must | M4 |
| Fit score with explanation (semantic CV ↔ job match) | Must | M5 |
| Application tracker (statuses, notes, history) | Must | M1 |
| Master CV as structured data + PDF in the user's design | Must | M1, M6 |
| Tailored CV with validator (no invented experience) | Must | M6 |
| Cover letter generation (streamed, editable) | Must | M6 |
| Assistant chat with tools | Should | M6 |
| Evals + LLM observability | Should | M7 |
| Voice mock interview | Should | M8 |
| Cloud deployment with daily scheduled scrape | Should | M9 |
| Multiple profiles (e.g. partner's search) | Should | M1 |
| Inbox sync: classify application emails, update the tracker | Could | M10 |
| Multi-LLM routing for cost and latency | Could | M10 |
| Auto-apply / form filling | **Won't** | Against job-board terms, risks accounts; applications stay human-sent |
| Scraping behind logins or around bot protection | **Won't** | Legal and ethical line |

### 6.2 Key user stories

- *As a candidate*, I want to see only jobs open to someone in my country, so I don't waste time on US-only roles.
- *As a candidate*, I want to see **why** a job was marked eligible or not (the quoted sentence from the description), so I can trust the filter.
- *As a candidate*, I want red flags (pay-to-apply, crypto-only pay, anonymous agency, US-hours night shifts) highlighted before I apply.
- *As a candidate*, I want a tailored CV that only reorders and rephrases my real experience, and a clear list of what changed, so I can send it with confidence.
- *As a candidate*, I want a cover letter that states my gaps honestly in one sentence instead of bluffing.
- *As a candidate*, I want to mark jobs applied, rejected, not relevant or expired, so my feed only shows what's left.
- *As a candidate*, I want to ask the assistant "what should I apply to today?" and get a ranked, explained shortlist.
- *As a candidate*, I want to practise a voice interview for a specific job and get feedback on weak answers.
- *As a second user*, I want my own searches, keywords and CV without seeing my partner's data.

## 7. Success metrics

**North-star metric:** *qualified applications sent per week*, meaning applications to jobs that are eligible and fit-scored, with a validated tailored CV.

| Metric | Target (v1, personal use) |
|---|---|
| Time from "open app" to "application ready" | < 5 minutes |
| Share of shown jobs actually open to the user | > 90% (vs ~70% with regex rules) |
| Tailoring-honesty eval pass rate | 100% on the golden set; 0 invented facts reaching the user |
| Job-analysis accuracy (eligibility, US hours, red flags) | ≥ 90% on the golden set |
| Daily scrape success | ≥ 90% of sources succeed |
| Voice interview time to first audio | < 1.5 s p50 after the user stops speaking |
| LLM cost | < $10/month at personal scale |

## 8. Business model (if it became a product)

- **Freemium:** free feed and tracker; paid tier ($10–15/month) for AI analysis, tailoring, letters and voice interviews.
- **Cost of goods:** LLM analysis only on pre-filtered jobs, caching by content hash, and a small model for analysis and a strong one for writing. Target AI cost under 20% of subscription revenue.
- **Never charge to apply,** never sell candidate data. That's the trust position against the pay-to-apply boards.
- **Channels:** remote-work communities, Telegram/LinkedIn groups for engineers in the CIS and Caucasus, word of mouth.

*For now this is a portfolio and personal-use project; the model exists to frame product decisions (cost guardrails, trust, scope).*

## 9. Non-functional requirements

- **Honesty:** tailored CVs pass a deterministic validator against the master CV; failures never reach the user silently.
- **Respectful scraping:** public pages only, rate limits per source, back-off on 429, no bot-protection bypassing, a source allow-list with a documented reason per source.
- **Privacy:** CVs and applications are personal data. Stored in the user's own database, never committed to the repo, and never sent anywhere except the configured LLM provider. Secrets via environment and Key Vault.
- **Performance:** API p95 < 300 ms for reads; streaming starts in < 1 s for letters; voice first-audio < 1.5 s p50.
- **Reliability:** one failing source never fails a scrape; offline or mostly-failed runs keep the previous results.
- **Observability:** every LLM call traced (Langfuse) with cost; service metrics in Azure Monitor; an alert on scrape failure.
- **Cost:** daily token budget per feature; a monthly Azure budget alert.
- **Quality:** typed Python (`mypy --strict`), tests for every feature, scrapers tested against recorded fixtures, evals in CI for prompt changes.

## 10. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| A source changes its HTML or API | Missing jobs | Adapter per source, fixture tests, per-source health in the dashboard, graceful failure |
| Rate limits or blocking (LinkedIn) | Partial results | Polite delays, back-off, fewer combined queries, cached results |
| LLM invents experience | Damaged credibility for the user | Deterministic validator + evals + human review before sending |
| LLM mis-judges eligibility | Wasted applications or missed jobs | Quote the evidence, keep the regex pre-filter as a second signal, golden-set evals |
| LLM / Azure cost creep | Budget overrun | Pre-filter, caching, small models for analysis, budgets and alerts |
| Terms-of-service issues | Account bans, legal | Public pages only, no auto-apply, no login scraping, documented source policy |
| Scope creep | Never finishing | Milestones with acceptance criteria; MoSCoW; "Won't" list above |

## 11. Roadmap

| Phase | Milestones | Outcome |
|---|---|---|
| **Foundation** (weeks 1–2) | M0, M1 | Data model, legacy import, jobs UI + tracker at parity with the script |
| **Discovery engine** (weeks 3–5) | M2, M3 | Async scraper as a gRPC streaming service, live progress |
| **Intelligence** (weeks 6–8) | M4, M5 | LLM job analysis, embeddings, fit score with explanations |
| **Applications** (weeks 9–11) | M6, M7 | Assistant, honest tailoring, letters, evals and observability |
| **Interview** (weeks 12–13) | M8 | Voice mock interview with latency tracking |
| **Production** (weeks 14–15) | M9 | Containers, Azure DevOps CI/CD, Azure deployment, monitoring |
| **Scale** (later) | M10 | Multi-LLM routing, Kubernetes, inbox sync |

Week estimates assume part-time evenings; the backlog lives on the GitHub Project board.

## 12. Open questions

- Which LLM tiers give the best cost/quality split for analysis vs writing? (Decided by evals in M7/M10.)
- How should the fit score combine keyword, semantic and analysis signals? (Tuned against the user's own accept/reject history.)
- Should inbox sync update the tracker automatically or only suggest changes? (Default: suggest, the user confirms.)
- Which sources are worth the maintenance cost? (Decided from per-source yield of applied-to jobs.)
