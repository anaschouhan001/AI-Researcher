import { CalendarDays } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { TimelineEvent } from "@/lib/types";
import { formatDate } from "@/lib/utils";

export interface TimelineProps {
  events: TimelineEvent[];
}

export function Timeline({ events }: TimelineProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <CalendarDays className="h-4 w-4 text-pink-400" aria-hidden="true" />
          Timeline
        </CardTitle>
      </CardHeader>
      <CardContent>
        {events.length === 0 ? (
          <p className="text-sm text-pink-400">No timeline events were extracted.</p>
        ) : (
          <ol className="relative ml-3 space-y-6 border-l-2 border-pink-200 pl-6">
            {events.map((event, i) => (
              <li key={`${event.date}-${i}`} className="relative">
                <span
                  className="absolute -left-[31px] top-1 h-2.5 w-2.5 rounded-full border-2 border-white bg-pink-400"
                  aria-hidden="true"
                />
                <time className="text-xs font-semibold uppercase tracking-wide text-fuchsia-500">
                  {formatDate(event.date)}
                </time>
                <p className="mt-1 text-sm leading-6 text-pink-950/90">{event.event}</p>
                {event.source && (
                  <p className="mt-0.5 text-[11px] text-pink-400">Source: {event.source}</p>
                )}
              </li>
            ))}
          </ol>
        )}
      </CardContent>
    </Card>
  );
}
