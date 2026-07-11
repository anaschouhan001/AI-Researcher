# ResearchGPT Architecture

## Overview

ResearchGPT is a layered, agentic research platform. Every layer depends only
on the layer below it and communicates through typed contracts
(`app/schemas/research.py`).

```
┌─────────────────────────────────────────────────────┐
│ Frontend (Next.js) — polls job status, renders result│
└──────────────────────┬──────────────────────────────┘
                       │ REST /api/v1
┌──────────────────────▼──────────────────────────────┐
│ API layer (FastAPI) — auth, jobs, downloads          │
├─────────────────────────────────────────────────────┤
│ Service layer — job lifecycle, dispatch              │
│   dev: in-process asyncio · prod: Celery + Redis     │
├─────────────────────────────────────────────────────┤
│ Agent pipeline (LangGraph)                           │
│  Planner → Research → Retriever → FactChecker        │
│   → Writer → Visualizer → Podcaster → Reporter       │
├──────────────┬──────────────┬───────────────────────┤
│ Sources (13) │ RAG (Chroma) │ Providers (LLM router) │
├──────────────┴──────────────┴───────────────────────┤
│ Core: config · logging · cache · http · security     │
└─────────────────────────────────────────────────────┘
```

## The agent pipeline

State (`agents/state.py`) flows through eight nodes; each node is an agent
class with independent prompts, memory, retries and structured-output parsing.

| Agent | Input | Output | Notes |
|---|---|---|---|
| Planner | topic, depth | sub-questions, queries, source categories | always keeps background/web/academic/news in play |
| Research | plan | deduplicated `SourceDocument[]` | fans out across adapters concurrently; failures isolated per source |
| Retriever | documents | `context_blocks` | chunks → embeds → ChromaDB; hybrid search per sub-question |
| Fact Checker | context | claim scores, conflicts, overall confidence | caps confidence at 70 when only one source responded |
| Writer | verified facts + context | exec summary, cited markdown report, insights, timeline, stats | every paragraph must end with `[source]` tags |
| Visualizer | documents + context | charts, knowledge graph, mind map | numeric charts computed deterministically in Python — the LLM never invents numbers |
| Podcaster | draft | WAV podcast | two-host script → Sarvam AI TTS; optional, never fails the run |
| Reporter | everything | `ResearchResult` + report files | validates all LLM output through pydantic, drops malformed entries |

## Resilience model

- **HTTP**: single shared `httpx` pool; tenacity exponential backoff on
  timeouts, 5xx and 429 (`core/http.py`).
- **Sources**: `SourceAdapter.search()` catches everything — a dead API returns
  `[]` and the run continues with the remaining sources.
- **LLM**: `LLMRouter` fails over provider-by-provider in configured priority;
  malformed JSON triggers a repair-prompt retry (max 3).
- **Cache**: Redis unavailable ⇒ cache silently no-ops.
- **DB**: configured engine unreachable ⇒ local SQLite fallback.
- **Stages**: core stages retry twice with backoff; enhancement stages
  (visuals, podcast) degrade gracefully instead.

## Data & caching

- SQLite (default) stores users and research jobs (result as JSON).
- ChromaDB persists one collection per job (`research_{job_id}`) — retrieval
  never bleeds between topics.
- Redis caches source responses (24 h; news 1 h; repo stats 6 h) keyed by
  SHA-256 of `(source, query, limit)`.

## Observability

`structlog` everywhere: JSON in production, console in dev. Every LLM call
logs provider, model, latency, input/output tokens. Every source fetch logs
latency and document count. Every HTTP request logs method/path/status/latency.

## Security

- JWT (HS256) auth; bcrypt password hashing.
- All secrets via `.env` (pydantic-settings); nothing hardcoded.
- Report downloads sanitize filenames; job IDs are UUIDv4.
