import * as React from "react";
import { cn } from "@/lib/utils";

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  /** 0-100 */
  value: number;
}

function Progress({ value, className, ...props }: ProgressProps) {
  const clamped = Math.min(100, Math.max(0, value));
  return (
    <div
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(clamped)}
      className={cn(
        "relative h-3 w-full overflow-hidden rounded-full border border-pink-200 bg-pink-100",
        className
      )}
      {...props}
    >
      <div
        className="h-full rounded-full bg-gradient-to-r from-pink-400 via-fuchsia-400 to-rose-400 bg-[length:200%_auto] animate-gradient-x transition-[width] duration-700 ease-out"
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}

export { Progress };
