# ResearchGPT — AI Research Platform

An enterprise-grade AI Research Analyst. Give it any topic and it performs
comprehensive multi-source research — gathering evidence from 13 verified
sources, cross-checking facts, scoring confidence, generating charts and a
knowledge graph, writing a fully-cited report, and voicing an AI podcast.

**This is not a chatbot.** It is an agentic pipeline:

```
Planner → Research → Retriever → Fact Checker → Writer → Visualization → Podcast → Report
```

## Features

- **13 modular research sources** — Wikipedia, SerpAPI, Tavily, arXiv, Semantic
  Scholar, CrossRef, GitHub, HuggingFace, Kaggle, GNews, NewsAPI, PubMed, OpenAlex
- **Multi-LLM provider abstraction** — Gemini → OpenRouter → Groq → Ollama with
  automatic failover; switching models is pure configuration
- **RAG** — ChromaDB vector store, sentence-transformer embeddings, sentence-aware
  chunking, hybrid (vector + BM25) search with reciprocal rank fusion, source filtering
- **Fact verification** — cross-source claim checking, conflict detection with
  "likely correct" resolution, per-claim and overall confidence scores
- **Visualizations** — charts built deterministically from real API data
  , LLM knowledge graph,
  Mermaid mind map
- **Reports** — Markdown / HTML / PDF / DOCX with citations on every paragraph
- **AI podcast** — two-host script voiced by Sarvam AI (English + Hindi)
- **Production hygiene** — structured logging (latency + token usage), Redis
  caching with graceful degradation, exponential-backoff retries, JWT auth,
  Celery workers, Docker Compose, tests with mocked APIs

## Quick start (development)

```bash
# 1. Configure
cp .env.example .env        # add your API keys (see below)

# 2. Backend
cd backend
python -m venv .venv && .venv\Scripts\activate    # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload                     # http://localhost:8000/docs

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev                                       # http://localhost:3000
```

The database is **SQLite** by default (zero setup). Redis is optional in
development — without it the cache simply no-ops. Jobs run in-process unless
`USE_CELERY=true`.

## Quick start (Docker)

```bash
docker compose up --build
# frontend http://localhost:3000 · API http://localhost:8000/docs
```

## API keys

Set in `.env` (never hardcoded, never committed):

| Key | Needed for | Free tier |
|---|---|---|
| `GOOGLE_API_KEY` | Gemini LLM + embeddings | yes |
| `OPENROUTER_API_KEY` | LLM fallback (Claude/DeepSeek/Qwen/...) | yes |
| `GROQ_API_KEY` | fast LLM fallback | yes |
| `SERPAPI_KEY`, `TAVILY_API_KEY` | web search | yes |
| `GITHUB_TOKEN`, `HUGGINGFACE_TOKEN` | higher rate limits | yes |
| `GNEWS_API_KEY`, `NEWS_API_KEY` | news | yes |
| `SARVAM_API_KEY` | podcast TTS | yes |
| `KAGGLE_USERNAME`/`KAGGLE_KEY`, `SEMANTIC_SCHOLAR_KEY`, `PUBMED_API_KEY` | optional | yes |

Wikipedia, arXiv, CrossRef, OpenAlex, PubMed, Semantic Scholar, GitHub and
HuggingFace all work **without any key**, so the platform is functional with
just one LLM key.

## Example

```
POST /api/v1/research
{"topic": "Quantum Computing in Healthcare", "depth": "standard", "language": "en"}
```

Returns a `job_id`; poll `GET /api/v1/research/{job_id}` for progress through the
agent stages, then download `report?format=pdf` or stream the `podcast`.

## Project structure

```
backend/app/
  api/            FastAPI routes, JWT deps
  agents/         LangGraph pipeline: planner, researcher, retriever,
                  fact_checker, writer, visualizer, podcaster, reporter
  providers/      LLM abstraction: gemini, openrouter, groq, ollama + router
  sources/        13 source adapters + registry
  retrieval/      chunking, embeddings, ChromaDB, hybrid search
  services/       research job lifecycle
  visualizations/ deterministic chart builders
  reports/        markdown/html/pdf/docx generation
  audio/          Sarvam AI TTS
  database/       SQLAlchemy models + async session (SQLite default)
  workers/        Celery app + tasks
  prompts/        every agent prompt in one place
  core/           config, logging, cache, http, security, exceptions
backend/tests/    unit + integration tests (respx-mocked APIs)
frontend/         Next.js 14 + TypeScript + Tailwind + Chart.js + React Flow
docs/             architecture & extension guides
docker/           Dockerfiles
```

## Extending

- **New research source** — one file subclassing `SourceAdapter` + one line in
  `sources/registry.py`. See `docs/ADDING_SOURCES.md`.
- **New LLM provider** — subclass `LLMProvider` (or `OpenAICompatibleProvider`)
  + register in `providers/factory.py`.

## Testing

```bash
cd backend
pytest            # all external APIs are mocked; no network needed
```
