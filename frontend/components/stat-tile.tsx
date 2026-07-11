import { cn } from "@/lib/utils";

export interface StatTileProps {
  label: string;
  value: string;
  source?: string;
  className?: string;
}

/** A single headline statistic — value first, label beneath, source as provenance. */
export function StatTile({ label, value, source, className }: StatTileProps) {
  return (
    <div
      className={cn(
        "glass flex flex-col justify-between gap-2 rounded-3xl p-4 transition-all duration-300 hover:-translate-y-0.5 hover:border-pink-400/60",
        className
      )}
    >
      <div>
        <p className="break-words text-xl font-bold text-gradient sm:text-2xl">{value}</p>
        <p className="mt-1 text-xs font-semibold text-pink-600">{label}</p>
      </div>
      {source && (
        <p className="truncate text-[11px] text-pink-400" title={source}>
          Source: {source}
        </p>
      )}
    </div>
  );
}
