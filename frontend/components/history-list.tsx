"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, History, Inbox } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api, ApiError } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import type { JobStatus, ResearchJob } from "@/lib/types";
import { formatDate } from "@/lib/utils";

const STATUS_BADGE: Record<JobStatus, { label: string; variant: "success" | "info" | "danger" | "secondary" }> = {
  completed: { label: "Completed 🌸", variant: "success" },
  running: { label: "Running ✨", variant: "info" },
  queued: { label: "Queued 💤", variant: "secondary" },
  failed: { label: "Failed 💔", variant: "danger" },
};

export function HistoryList() {
  const [jobs, setJobs] = useState<ResearchJob[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [authed, setAuthed] = useState<boolean | null>(null);

  useEffect(() => {
    const isAuthed = isAuthenticated();
    setAuthed(isAuthed);
    if (!isAuthed) return;

    const controller = new AbortController();
    api
      .listJobs(controller.signal)
      .then((list) => {
        // Newest first when timestamps exist.
        const sorted = [...list].sort((a, b) => {
          if (!a.created_at || !b.created_at) return 0;
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        });
        setJobs(sorted);
      })
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError(err instanceof ApiError ? err.message : "Could not load research history.");
      });
    return () => controller.abort();
  }, []);

  // Not signed in (or still deciding): the landing page reads better without an empty panel.
  if (authed === null || authed === false) return null;

  return (
    <section aria-labelledby="history-heading" className="w-full">
      <div className="mb-4 flex items-center gap-2">
        <History className="h-4 w-4 text-pink-400" aria-hidden="true" />
        <h2 id="history-heading" className="text-sm font-bold uppercase tracking-wider text-pink-500">
          Recent research 💕
        </h2>
      </div>

      {error && (
        <Card>
          <CardContent className="p-5 text-sm text-rose-500">{error}</CardContent>
        </Card>
      )}

      {!error && jobs === null && (
        <div className="space-y-3">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      )}

      {!error && jobs !== null && jobs.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center gap-2 p-8 text-center">
            <Inbox className="h-8 w-8 text-pink-300 animate-bounce-soft" aria-hidden="true" />
            <p className="text-sm text-pink-600">No research yet, cutie! 🎀</p>
            <p className="text-xs text-pink-400">
              Enter a topic above and your investigations will appear here.
            </p>
          </CardContent>
        </Card>
      )}

      {!error && jobs !== null && jobs.length > 0 && (
        <ul className="space-y-3">
          {jobs.map((job) => {
            const badge = STATUS_BADGE[job.status] ?? STATUS_BADGE.queued;
            return (
              <li key={job.job_id}>
                <Link
                  href={`/research/${job.job_id}`}
                  className="group flex items-center justify-between gap-4 rounded-3xl border-2 border-pink-200 bg-white/80 px-4 py-3.5 shadow-candy transition-all duration-300 hover:-translate-y-0.5 hover:border-pink-400 hover:shadow-candy-lg"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-pink-800 group-hover:text-pink-600">
                      {job.topic || "Untitled research"}
                    </p>
                    <p className="mt-0.5 text-xs text-pink-400">
                      {job.created_at ? formatDate(job.created_at) : `Job ${job.job_id.slice(0, 8)}`}
                      {job.status === "running" && ` · ${Math.round(job.progress)}%`}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-3">
                    <Badge variant={badge.variant}>{badge.label}</Badge>
                    <ArrowRight
                      className="h-4 w-4 text-pink-300 transition-transform group-hover:translate-x-0.5 group-hover:text-pink-500"
                      aria-hidden="true"
                    />
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
