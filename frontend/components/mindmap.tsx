"use client";

import { useEffect, useId, useRef, useState } from "react";
import { GitFork, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export interface MindmapProps {
  /** Mermaid `mindmap` syntax. */
  code: string;
}

export default function Mindmap({ code }: MindmapProps) {
  const reactId = useId();
  const containerRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error" | "empty">(
    code.trim() ? "loading" : "empty"
  );

  useEffect(() => {
    if (!code.trim()) {
      setStatus("empty");
      return;
    }

    let cancelled = false;
    setStatus("loading");

    (async () => {
      try {
        const mermaid = (await import("mermaid")).default;
        mermaid.initialize({
          startOnLoad: false,
          theme: "base",
          darkMode: false,
          securityLevel: "strict",
          themeVariables: {
            background: "#fff0f6",
            primaryColor: "#ffe3ee",
            primaryTextColor: "#7d1a43",
            primaryBorderColor: "#f9498c",
            lineColor: "#f472b6",
            fontFamily: "system-ui, sans-serif",
          },
        });
        // Mermaid ids must be valid CSS selectors — strip the colons React adds.
        const renderId = `mindmap-${reactId.replace(/[^a-zA-Z0-9]/g, "")}`;
        const { svg } = await mermaid.render(renderId, code);
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
          setStatus("ready");
        }
      } catch {
        if (!cancelled) setStatus("error");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [code, reactId]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <GitFork className="h-4 w-4 text-pink-400" aria-hidden="true" />
          Mind map
        </CardTitle>
      </CardHeader>
      <CardContent>
        {status === "empty" && (
          <p className="text-sm text-pink-400">No mind map was generated.</p>
        )}
        {status === "loading" && (
          <div className="flex h-48 items-center justify-center gap-2 text-sm text-pink-400">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            Rendering mind map…
          </div>
        )}
        {status === "error" && (
          <p className="rounded-2xl border-2 border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-600">
            The mind map could not be rendered (invalid Mermaid syntax).
          </p>
        )}
        <div
          ref={containerRef}
          className="mermaid-container overflow-x-auto"
          style={{ display: status === "ready" ? "block" : "none" }}
          aria-label="Mind map diagram"
        />
      </CardContent>
    </Card>
  );
}
