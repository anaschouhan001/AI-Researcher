"use client";

import { useEffect, useRef, useState } from "react";
import { AudioLines, Loader2, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { api, ApiError } from "@/lib/api";
import type { ResearchLanguage } from "@/lib/types";

export interface PodcastPlayerProps {
  jobId: string;
  available: boolean;
  defaultLanguage?: ResearchLanguage;
}

export function PodcastPlayer({ jobId, available, defaultLanguage = "en" }: PodcastPlayerProps) {
  const [language, setLanguage] = useState<ResearchLanguage>(defaultLanguage);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const urlRef = useRef<string | null>(null);

  // Revoke the object URL when it changes or on unmount.
  useEffect(() => {
    urlRef.current = audioUrl;
    return () => {
      if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    };
  }, [audioUrl]);

  async function loadPodcast() {
    setLoading(true);
    setError(null);
    setAudioUrl(null);
    try {
      const url = await api.fetchPodcastUrl(jobId, language);
      setAudioUrl(url);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Could not load the podcast audio. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  if (!available) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center gap-3 p-12 text-center">
          <AudioLines className="h-10 w-10 text-pink-300" aria-hidden="true" />
          <p className="text-sm font-semibold text-pink-700">Podcast not available 🎧</p>
          <p className="max-w-md text-xs text-pink-400">
            A narrated podcast was not generated for this research run.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <AudioLines className="h-4 w-4 text-pink-400" aria-hidden="true" />
          Research podcast 🎧
        </CardTitle>
        <CardDescription>
          A narrated walkthrough of the findings, generated from the final report.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="w-full space-y-1.5 sm:w-52">
            <label htmlFor="podcast-language" className="text-sm font-semibold text-pink-700">
              Language
            </label>
            <Select
              id="podcast-language"
              value={language}
              onChange={(e) => setLanguage(e.target.value as ResearchLanguage)}
              disabled={loading}
            >
              <option value="en">English</option>
              <option value="hi">हिन्दी (Hindi)</option>
            </Select>
          </div>
          <Button onClick={loadPodcast} disabled={loading}>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              <Play className="h-4 w-4" aria-hidden="true" />
            )}
            {loading ? "Loading audio…" : audioUrl ? "Reload" : "Load podcast"}
          </Button>
        </div>

        {error && (
          <p role="alert" className="rounded-2xl border-2 border-rose-300 bg-rose-50 px-3 py-2 text-sm text-rose-600">
            {error}
          </p>
        )}

        {audioUrl && (
          // eslint-disable-next-line jsx-a11y/media-has-caption -- generated speech, no caption track from API
          <audio controls src={audioUrl} className="w-full" preload="metadata">
            Your browser does not support audio playback.
          </audio>
        )}
      </CardContent>
    </Card>
  );
}
