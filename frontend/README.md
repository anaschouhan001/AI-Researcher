# ResearchGPT — Frontend

Production-grade Next.js 14 (App Router) frontend for **ResearchGPT**, an AI research
platform. Users submit a topic, a multi-agent pipeline (Planner → Research → Retriever →
Fact Checker → Writer → Visualization → Podcast → Report) investigates it, and the app
presents a cited report with charts, timeline, knowledge graph, mind map, conflict
analysis, confidence scoring, podcast playback and multi-format export.

## Requirements

- Node.js 18.17+ (Node 20 recommended)
- A running ResearchGPT FastAPI backend (base path `/api/v1`)

## Getting started

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Base URL of the FastAPI backend (without `/api/v1`) |

Create a `.env.local` to override:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start the dev server |
| `npm run build` | Production build |
| `npm run start` | Serve the production build |
| `npm run lint` | ESLint (next/core-web-vitals) |

## Architecture

```
app/
  layout.tsx            Root layout: navbar, footer, dark theme
  page.tsx              Landing: hero, research form, feature grid, history
  login/page.tsx        JWT sign-in
  register/page.tsx     Account creation
  research/[id]/page.tsx  Core screen: live pipeline tracker (2.5s polling)
                          -> tabbed results (Overview / Report / Sources /
                          Visuals / Conflicts / Podcast / Export)
components/
  ui/                   Hand-written shadcn-style primitives
  chart-panel.tsx       Chart.js renderers (bar/line/pie/doughnut)
  knowledge-graph.tsx   React Flow entity graph
  mindmap.tsx           Mermaid mindmap renderer
  ...                   Pipeline tracker, gauge, sources, conflicts, podcast, export
lib/
  api.ts                Fetch wrapper: Bearer auth, 401 -> /login, blob downloads
  auth.ts               localStorage token store
  types.ts              API contract types (ResearchResult, ResearchJob, ...)
  utils.ts              cn(), formatting, confidence color coding
```

Notes:

- The auth token is stored in `localStorage` under `researchgpt_token`; every API call
  attaches it as a `Bearer` header, and any 401 clears it and redirects to `/login`.
- Chart.js, React Flow and Mermaid components are loaded with `next/dynamic`
  (`ssr: false`) — they only ship to and run in the browser.
- Report and podcast downloads are fetched as authenticated blobs, so the JWT is never
  leaked into plain `<a href>` URLs.
- Confidence scores are color-coded: **>= 85 green**, **>= 60 amber**, otherwise **red**.
