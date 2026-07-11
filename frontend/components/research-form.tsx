"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Loader2, Search, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { api, ApiError } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import type { ResearchDepth, ResearchLanguage } from "@/lib/types";

const DEPTH_HINTS: Record<ResearchDepth, string> = {
  quick: "~2 min · headline scan across key sources 🌸",
  standard: "~5 min · balanced multi-source investigation 💖",
  deep: "~15 min · exhaustive pipeline with fact-checking 👑",
};

export function ResearchForm() {
  const router = useRouter();
  const [topic, setTopic] = useState("");
  const [depth, setDepth] = useState<ResearchDepth>("standard");
  const [language, setLanguage] = useState<ResearchLanguage>("en");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const trimmed = topic.trim();
    if (!trimmed) return;

    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }

    setError(null);
    setLoading(true);
    try {
      const res = await api.startResearch(trimmed, depth, language);
      router.push(`/research/${res.job_id}`);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not start research. Please try again."
      );
      setLoading(false);
    }
  }

  return (
    <Card className="border-pink-300/60 bg-white/85 shadow-candy-lg">
      <CardContent className="p-5 sm:p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label htmlFor="topic" className="flex items-center gap-1.5 text-sm font-semibold text-pink-700">
              <Sparkles className="h-3.5 w-3.5 text-pink-400 animate-sparkle" aria-hidden="true" />
              Research topic
            </label>
            <Input
              id="topic"
              placeholder='e.g. "State of small language models in 2026" ✨'
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              maxLength={500}
              className="h-12 text-base"
              autoFocus
            />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-1.5">
              <label htmlFor="depth" className="text-sm font-semibold text-pink-700">
                Depth
              </label>
              <Select
                id="depth"
                value={depth}
                onChange={(e) => setDepth(e.target.value as ResearchDepth)}
              >
                <option value="quick">Quick</option>
                <option value="standard">Standard</option>
                <option value="deep">Deep</option>
              </Select>
              <p className="text-xs text-pink-400">{DEPTH_HINTS[depth]}</p>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="language" className="text-sm font-semibold text-pink-700">
                Language
              </label>
              <Select
                id="language"
                value={language}
                onChange={(e) => setLanguage(e.target.value as ResearchLanguage)}
              >
                <option value="en">English</option>
                <option value="hi">हिन्दी (Hindi)</option>
              </Select>
              <p className="text-xs text-pink-400">Report and podcast language.</p>
            </div>
          </div>

          {error && (
            <p role="alert" className="rounded-2xl border-2 border-rose-300 bg-rose-50 px-3 py-2 text-sm text-rose-600">
              {error}
            </p>
          )}

          <Button type="submit" size="lg" className="w-full" disabled={loading || !topic.trim()}>
            {loading ? (
              <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
            ) : (
              <Search className="h-5 w-5" aria-hidden="true" />
            )}
            {loading ? "Dispatching agents… 💌" : "Start deep research 💖"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
