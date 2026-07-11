/** Shared domain types for the ResearchGPT frontend. */

export type ResearchDepth = "quick" | "standard" | "deep";
export type ResearchLanguage = "en" | "hi";
export type JobStatus = "queued" | "running" | "completed" | "failed";
export type ReportFormat = "markdown" | "pdf" | "docx" | "html";
export type ChartType = "bar" | "pie" | "line" | "doughnut";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface StartResearchResponse {
  job_id: string;
  status: "queued";
}

export interface TimelineEvent {
  date: string;
  event: string;
  source: string;
}

export interface NewsItem {
  title: string;
  url: string;
  source: string;
  published_at: string;
  summary: string;
}

export interface Paper {
  title: string;
  authors: string[];
  year: number | null;
  url: string;
  citations: number | null;
  abstract: string;
  source: string;
}

export interface GithubRepo {
  name: string;
  url: string;
  stars: number;
  description: string;
  language: string | null;
}

export interface HuggingFaceModel {
  id: string;
  url: string;
  downloads: number;
  likes: number;
  task: string | null;
}

export interface Dataset {
  name: string;
  url: string;
  source: string;
  description: string;
}

export interface Statistic {
  label: string;
  value: string;
  source: string;
}

export interface ChartDatasetSpec {
  label: string;
  data: number[];
}

export interface ChartSpec {
  id: string;
  type: ChartType;
  title: string;
  labels: string[];
  datasets: ChartDatasetSpec[];
}

export interface KnowledgeGraphNode {
  id: string;
  label: string;
  group: string;
}

export interface KnowledgeGraphEdge {
  source: string;
  target: string;
  label: string;
}

export interface KnowledgeGraph {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
}

export interface Citation {
  id: number;
  source: string;
  title: string;
  url: string;
}

export interface ClaimScore {
  claim: string;
  score: number;
  sources: string[];
}

export interface Confidence {
  overall: number;
  rationale: string;
  claim_scores: ClaimScore[];
}

export interface ConflictPosition {
  statement: string;
  sources: string[];
}

export interface Conflict {
  claim: string;
  positions: ConflictPosition[];
  likely_correct: string;
  evidence: string;
}

export interface ResearchResult {
  topic: string;
  executive_summary: string;
  report_markdown: string;
  key_insights: string[];
  timeline: TimelineEvent[];
  news: NewsItem[];
  papers: Paper[];
  github_repos: GithubRepo[];
  huggingface_models: HuggingFaceModel[];
  datasets: Dataset[];
  statistics: Statistic[];
  charts: ChartSpec[];
  knowledge_graph: KnowledgeGraph;
  /** Mermaid `mindmap` syntax. */
  mindmap_mermaid: string;
  citations: Citation[];
  confidence: Confidence;
  conflicts: Conflict[];
  podcast_available: boolean;
}

export interface ResearchJob {
  job_id: string;
  topic: string;
  status: JobStatus;
  /** 0-100 */
  progress: number;
  current_stage: string;
  error?: string;
  result?: ResearchResult;
  created_at?: string;
  depth?: ResearchDepth;
  language?: ResearchLanguage;
}
