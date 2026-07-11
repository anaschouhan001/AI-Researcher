"use client";

import dynamic from "next/dynamic";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { AlertTriangle, ArrowLeft, Lightbulb, RefreshCw } from "lucide-react";
import { ConfidenceGauge, ConfidencePill } from "@/components/confidence-gauge";
import { ConflictsPanel } from "@/components/conflicts-panel";
import { ExportPanel } from "@/components/export-panel";
import { MarkdownView } from "@/components/markdown-view";
import { PipelineProgress } from "@/components/pipeline-progress";
import { PodcastPlayer } from "@/components/podcast-player";
import { SourcesPanel } from "@/components/source-cards";
import { StatTile } from "@/components/stat-tile";
import { Timeline } from "@/components/timeline";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api, ApiError } from "@/lib/api";
import type { ResearchJob } from "@/lib/types";
import { confidenceColor, normalizeConfidence } from "@/lib/utils";

// Chart.js, React Flow and Mermaid all touch browser APIs — client-only chunks.
const ChartPanel = dynamic(() => import("@/components/chart-panel"), {
  ssr: false,
  loading: () => <Skeleton className="h-72 w-full" />,
});
const KnowledgeGraphView = dynamic(() => import("@/components/knowledge-graph"), {
  ssr: false,
  loading: () => <Skeleton className="h-[480px] w-full" />,
});
const Mindmap = dynamic(() => import("@/components/mindmap"), {
  ssr: false,
  loading: () => <Skeleton className="h-48 w-full" />,
});

const POLL_INTERVAL_MS = 2500;
const RETRY_INTERVAL_MS = 5000;

export default function ResearchPage({ params }: { params: { id: string } }) {
  const jobId = params.id;
  const [job, setJob] = useState<ResearchJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    async function poll() {
      try {
        const next = await api.getJob(jobId);
        if (cancelled) return;
        setJob(next);
        setError(null);
        if (next.status === "queued" || next.status === "running") {
          timer = setTimeout(poll, POLL_INTERVAL_MS);
        }
      } catch (err) {
        if (cancelled) return;
        if (err instanceof DOMException && err.name === "AbortError") return;
        const message =
          err instanceof ApiError ? err.message : "Something went wrong while loading this job.";
        setError(message);
        // Transient network failures keep retrying; hard API errors (404 etc.) stop.
        if (err instanceof ApiError && err.status === 0) {
          timer = setTimeout(poll, RETRY_INTERVAL_MS);
        }
      }
    }

    poll();
    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [jobId, reloadKey]);

  /* ---------------------------------------------------------------- */
  /* Error before any job data loaded                                  */
  /* ---------------------------------------------------------------- */
  if (error && !job) {
    return (
      <div className="mx-auto mt-16 max-w-lg">
        <Card>
          <CardContent className="flex flex-col items-center gap-4 p-10 text-center">
            <AlertTriangle className="h-10 w-10 text-amber-400" aria-hidden="true" />
            <div>
              <p className="text-base font-semibold text-pink-800">Could not load research job 💔</p>
              <p className="mt-1 text-sm text-pink-400">{error}</p>
            </div>
            <div className="flex gap-3">
              <Button variant="outline" onClick={() => { setError(null); setReloadKey((k) => k + 1); }}>
                <RefreshCw className="h-4 w-4" aria-hidden="true" />
                Retry
              </Button>
              <Link href="/">
                <Button variant="ghost">
                  <ArrowLeft className="h-4 w-4" aria-hidden="true" />
                  Back home
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  /* ---------------------------------------------------------------- */
  /* Initial loading                                                    */
  /* ---------------------------------------------------------------- */
  if (!job) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-9 w-2/3" />
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  /* ---------------------------------------------------------------- */
  /* Failed                                                             */
  /* ---------------------------------------------------------------- */
  if (job.status === "failed") {
    return (
      <div className="space-y-6">
        <PageHeader job={job} />
        <Card className="border-rose-300">
          <CardContent className="flex flex-col items-center gap-4 p-10 text-center">
            <AlertTriangle className="h-10 w-10 text-rose-400" aria-hidden="true" />
            <div>
              <p className="text-base font-semibold text-pink-800">Research failed 💔</p>
              <p className="mt-1 max-w-xl text-sm text-pink-400">
                {job.error || "The research pipeline encountered an unrecoverable error."}
              </p>
            </div>
            <Link href="/">
              <Button variant="outline">
                <ArrowLeft className="h-4 w-4" aria-hidden="true" />
                Start a new research
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  /* ---------------------------------------------------------------- */
  /* Queued / running — animated pipeline                               */
  /* ---------------------------------------------------------------- */
  if (job.status === "queued" || job.status === "running") {
    return (
      <div className="space-y-6">
        <PageHeader job={job} />
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Agent pipeline</CardTitle>
          </CardHeader>
          <CardContent>
            <PipelineProgress
              currentStage={job.current_stage}
              progress={job.progress}
              status={job.status}
            />
          </CardContent>
        </Card>
        {error && (
          <p className="text-center text-xs text-amber-400">
            Connection hiccup — retrying automatically… ({error})
          </p>
        )}
        <p className="text-center text-xs text-pink-400">
          This page refreshes automatically every few seconds. Feel free to leave and come back —
          the agents keep working server-side. 💖
        </p>
      </div>
    );
  }

  /* ---------------------------------------------------------------- */
  /* Completed                                                          */
  /* ---------------------------------------------------------------- */
  const result = job.result;
  if (!result) {
    return (
      <div className="space-y-6">
        <PageHeader job={job} />
        <Card>
          <CardContent className="p-10 text-center text-sm text-pink-400">
            The job is marked completed but no result payload was returned by the API.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader job={job} />

      <Tabs defaultValue="overview">
        <TabsList className="w-full justify-start">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="report">Report</TabsTrigger>
          <TabsTrigger value="sources">Sources</TabsTrigger>
          <TabsTrigger value="visuals">Visuals</TabsTrigger>
          <TabsTrigger value="conflicts">
            Conflicts
            {result.conflicts.length > 0 && (
              <span className="ml-1.5 rounded-full bg-amber-500/20 px-1.5 text-[10px] font-semibold text-amber-400">
                {result.conflicts.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="podcast">Podcast</TabsTrigger>
          <TabsTrigger value="export">Export</TabsTrigger>
        </TabsList>

        {/* ------------------------------ Overview ----------------- */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-sm">Executive summary</CardTitle>
              </CardHeader>
              <CardContent>
                {result.executive_summary ? (
                  <p className="whitespace-pre-line text-sm leading-7 text-pink-950/90">
                    {result.executive_summary}
                  </p>
                ) : (
                  <p className="text-sm text-pink-400">No executive summary available.</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Confidence</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col items-center gap-4">
                <ConfidenceGauge value={result.confidence.overall} />
                {result.confidence.rationale && (
                  <p className="text-center text-xs leading-5 text-pink-400">
                    {result.confidence.rationale}
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          {result.key_insights.length > 0 && (
            <Card className="mt-5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Lightbulb className="h-4 w-4 text-amber-300" aria-hidden="true" />
                  Key insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="grid grid-cols-1 gap-3 md:grid-cols-2">
                  {result.key_insights.map((insight, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-3 rounded-2xl border-2 border-pink-200 bg-pink-50/70 p-3.5"
                    >
                      <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-pink-200 text-[11px] font-bold text-pink-700">
                        {i + 1}
                      </span>
                      <span className="text-sm leading-6 text-pink-950/90">{insight}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {result.statistics.length > 0 && (
            <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {result.statistics.map((stat, i) => (
                <StatTile key={i} label={stat.label} value={stat.value} source={stat.source} />
              ))}
            </div>
          )}

          {result.confidence.claim_scores.length > 0 && (
            <Card className="mt-5">
              <CardHeader>
                <CardTitle className="text-sm">Claim-level confidence</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {result.confidence.claim_scores.map((claim, i) => {
                    const pct = normalizeConfidence(claim.score);
                    const color = confidenceColor(pct);
                    return (
                      <li key={i} className="rounded-2xl border-2 border-pink-200 bg-pink-50/70 p-3.5">
                        <div className="flex items-start justify-between gap-4">
                          <p className="text-sm leading-6 text-pink-950/90">{claim.claim}</p>
                          <span className={`shrink-0 text-sm font-bold tabular-nums ${color.text}`}>
                            {pct}%
                          </span>
                        </div>
                        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-pink-100">
                          <div
                            className="h-full rounded-full"
                            style={{ width: `${pct}%`, backgroundColor: color.hex }}
                          />
                        </div>
                        {claim.sources.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1.5">
                            {claim.sources.map((source, j) => (
                              <Badge key={j} variant="secondary">
                                {source}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* ------------------------------ Report ------------------- */}
        <TabsContent value="report">
          <Card>
            <CardContent className="p-6 sm:p-8">
              <MarkdownView markdown={result.report_markdown} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* ------------------------------ Sources ------------------ */}
        <TabsContent value="sources">
          <SourcesPanel result={result} />
        </TabsContent>

        {/* ------------------------------ Visuals ------------------ */}
        <TabsContent value="visuals">
          <div className="space-y-5">
            <ChartPanel charts={result.charts} />
            <Timeline events={result.timeline} />
            <KnowledgeGraphView graph={result.knowledge_graph} />
            <Mindmap code={result.mindmap_mermaid} />
          </div>
        </TabsContent>

        {/* ------------------------------ Conflicts ---------------- */}
        <TabsContent value="conflicts">
          <ConflictsPanel conflicts={result.conflicts} />
        </TabsContent>

        {/* ------------------------------ Podcast ------------------ */}
        <TabsContent value="podcast">
          <PodcastPlayer
            jobId={job.job_id}
            available={result.podcast_available}
            defaultLanguage={job.language ?? "en"}
          />
        </TabsContent>

        {/* ------------------------------ Export ------------------- */}
        <TabsContent value="export">
          <ExportPanel jobId={job.job_id} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

/* -------------------------------------------------------------------- */

function PageHeader({ job }: { job: ResearchJob }) {
  return (
    <div>
      <Link
        href="/"
        className="mb-3 inline-flex items-center gap-1.5 text-xs font-semibold text-pink-400 hover:text-pink-600"
      >
        <ArrowLeft className="h-3.5 w-3.5" aria-hidden="true" />
        All research
      </Link>
      <div className="flex items-center gap-4 rounded-3xl border-2 border-pink-200 bg-gradient-to-r from-pink-100/90 via-white/90 to-fuchsia-50/90 p-4 shadow-candy sm:p-5">
        <Image
          src="/cute-robot.jpg"
          alt="Research robot mascot"
          width={64}
          height={64}
          className="hidden h-16 w-16 shrink-0 rounded-2xl border-2 border-white object-cover shadow-candy sm:block"
        />
        <div className="min-w-0">
          <p className="text-[11px] font-bold uppercase tracking-widest text-pink-400">
            Research dossier 🎀
          </p>
          <div className="mt-0.5 flex flex-wrap items-center gap-x-4 gap-y-2">
            <h1 className="text-xl font-bold tracking-tight text-pink-800 sm:text-2xl">
              {job.topic || "Untitled research"}
            </h1>
            {job.status === "completed" && job.result && (
              <ConfidencePill value={job.result.confidence.overall} />
            )}
            {job.status === "running" && <Badge variant="info">Running · {Math.round(job.progress)}%</Badge>}
            {job.status === "queued" && <Badge variant="secondary">Queued</Badge>}
            {job.status === "failed" && <Badge variant="danger">Failed</Badge>}
          </div>
        </div>
      </div>
    </div>
  );
}
