import { CheckCircle2, Scale, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Conflict } from "@/lib/types";

export interface ConflictsPanelProps {
  conflicts: Conflict[];
}

export function ConflictsPanel({ conflicts }: ConflictsPanelProps) {
  if (conflicts.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center gap-3 p-12 text-center">
          <ShieldCheck className="h-10 w-10 text-emerald-500" aria-hidden="true" />
          <p className="text-sm font-semibold text-pink-800">No conflicting claims detected 🌸</p>
          <p className="max-w-md text-xs text-pink-400">
            The fact-checking agent did not find sources that materially contradict each other on
            this topic.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-5">
      {conflicts.map((conflict, i) => (
        <Card key={i}>
          <CardHeader>
            <CardTitle className="flex items-start gap-2 text-sm leading-6">
              <Scale className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" aria-hidden="true" />
              {conflict.claim}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              {conflict.positions.map((position, j) => (
                <div
                  key={j}
                  className="rounded-2xl border-2 border-pink-200 bg-pink-50/70 p-3.5"
                >
                  <p className="text-sm leading-6 text-pink-950/90">{position.statement}</p>
                  {position.sources.length > 0 && (
                    <div className="mt-2.5 flex flex-wrap gap-1.5">
                      {position.sources.map((source, k) => (
                        <Badge key={k} variant="secondary">
                          {source}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="rounded-2xl border-2 border-emerald-200 bg-emerald-50/70 p-3.5">
              <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-emerald-600">
                <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
                Most likely correct
              </p>
              <p className="mt-1.5 text-sm leading-6 text-pink-950/90">{conflict.likely_correct}</p>
              {conflict.evidence && (
                <p className="mt-2 text-xs leading-5 text-pink-500">
                  <span className="font-semibold text-pink-700">Evidence: </span>
                  {conflict.evidence}
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
