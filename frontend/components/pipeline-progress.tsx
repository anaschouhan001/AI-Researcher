"use client";

import Image from "next/image";
import { motion } from "framer-motion";
import {
  AudioLines,
  BarChart3,
  Check,
  ClipboardList,
  Database,
  FileText,
  PenLine,
  Search,
  ShieldCheck,
  type LucideIcon,
} from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface Stage {
  key: string;
  label: string;
  icon: LucideIcon;
  /** lowercase substrings matched against `current_stage` from the API */
  match: string[];
}

const STAGES: Stage[] = [
  { key: "planner", label: "Planner", icon: ClipboardList, match: ["plan"] },
  { key: "research", label: "Research", icon: Search, match: ["research", "search", "gather"] },
  { key: "retriever", label: "Retriever", icon: Database, match: ["retriev", "fetch", "collect"] },
  { key: "factcheck", label: "Fact Checker", icon: ShieldCheck, match: ["fact", "verif", "check"] },
  { key: "writer", label: "Writer", icon: PenLine, match: ["writ", "draft", "summar"] },
  { key: "visualization", label: "Visualization", icon: BarChart3, match: ["visual", "chart", "graph"] },
  { key: "podcast", label: "Podcast", icon: AudioLines, match: ["podcast", "audio", "voice"] },
  { key: "report", label: "Report", icon: FileText, match: ["report", "final", "export"] },
];

function activeStageIndex(currentStage: string, progress: number): number {
  const normalized = currentStage.toLowerCase();
  for (let i = STAGES.length - 1; i >= 0; i--) {
    if (STAGES[i].match.some((m) => normalized.includes(m))) return i;
  }
  // Unknown stage label: estimate from progress.
  return Math.min(
    STAGES.length - 1,
    Math.floor((Math.min(99, Math.max(0, progress)) / 100) * STAGES.length)
  );
}

export interface PipelineProgressProps {
  currentStage: string;
  progress: number;
  status: "queued" | "running";
}

export function PipelineProgress({ currentStage, progress, status }: PipelineProgressProps) {
  const activeIndex = status === "queued" ? -1 : activeStageIndex(currentStage, progress);

  return (
    <div className="grid items-center gap-6 lg:grid-cols-[220px_1fr] lg:gap-10">
      {/* Retro loading illustration keeps the wait cute */}
      <div className="flex justify-center">
        <div className="animate-float overflow-hidden rounded-3xl border-4 border-white shadow-candy-lg">
          <Image
            src="/retro-loading.jpg"
            alt="Retro loading window illustration"
            width={220}
            height={392}
            className="h-auto w-[150px] object-cover sm:w-[190px]"
          />
        </div>
      </div>

      <div className="space-y-7">
        <div className="space-y-2">
          <div className="flex items-baseline justify-between text-sm">
            <span className="font-semibold text-pink-700">
              {status === "queued" ? "Waiting in queue… 💤" : `${currentStage || "Working…"} ✨`}
            </span>
            <span className="tabular-nums font-bold text-pink-500">{Math.round(progress)}%</span>
          </div>
          <Progress value={status === "queued" ? 2 : progress} />
        </div>

        <ol className="grid grid-cols-2 gap-x-2 gap-y-6 sm:grid-cols-4">
        {STAGES.map((stage, i) => {
          const state = i < activeIndex ? "done" : i === activeIndex ? "active" : "pending";
          return (
            <li key={stage.key} className="flex flex-col items-center gap-2 text-center">
              <div className="relative">
                {state === "active" && (
                  <motion.span
                    className="absolute inset-0 rounded-full bg-pink-400/50"
                    animate={{ scale: [1, 1.55, 1], opacity: [0.55, 0, 0.55] }}
                    transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
                    aria-hidden="true"
                  />
                )}
                <span
                  className={cn(
                    "relative flex h-11 w-11 items-center justify-center rounded-full border-2 transition-colors",
                    state === "done" && "border-emerald-300 bg-emerald-50 text-emerald-500",
                    state === "active" && "border-pink-400 bg-pink-100 text-pink-600 animate-wiggle",
                    state === "pending" && "border-pink-200 bg-white text-pink-300"
                  )}
                >
                  {state === "done" ? (
                    <Check className="h-5 w-5" aria-hidden="true" />
                  ) : (
                    <stage.icon className="h-5 w-5" aria-hidden="true" />
                  )}
                </span>
              </div>
              <span
                className={cn(
                  "text-xs font-semibold leading-tight",
                  state === "done" && "text-emerald-500",
                  state === "active" && "text-pink-600",
                  state === "pending" && "text-pink-300"
                )}
              >
                {stage.label}
              </span>
            </li>
          );
        })}
        </ol>
      </div>
    </div>
  );
}
