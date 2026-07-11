"use client";

import { confidenceColor, normalizeConfidence } from "@/lib/utils";

export interface ConfidenceGaugeProps {
  /** Accepts 0-1 or 0-100. */
  value: number;
  size?: number;
  label?: string;
}

/** Radial percentage gauge, color-coded: >=85 green, >=60 amber, else red. */
export function ConfidenceGauge({ value, size = 148, label = "Confidence" }: ConfidenceGaugeProps) {
  const pct = normalizeConfidence(value);
  const color = confidenceColor(pct);

  const stroke = 11;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const dash = (pct / 100) * circumference;

  return (
    <div
      className="flex flex-col items-center"
      role="img"
      aria-label={`${label}: ${pct} out of 100 (${color.label})`}
    >
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90" aria-hidden="true">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(249, 168, 212, 0.3)"
            strokeWidth={stroke}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color.hex}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={`${dash} ${circumference - dash}`}
            style={{ transition: "stroke-dasharray 0.8s ease-out" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-bold tabular-nums ${color.text}`}>{pct}</span>
          <span className="text-[10px] font-medium uppercase tracking-wider text-pink-400">
            / 100
          </span>
        </div>
      </div>
      <span className={`mt-2 text-xs font-medium ${color.text}`}>{color.label}</span>
    </div>
  );
}

/** Compact inline confidence pill for headers. */
export function ConfidencePill({ value }: { value: number }) {
  const pct = normalizeConfidence(value);
  const color = confidenceColor(pct);
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm font-semibold ${color.bg} ${color.text}`}
      title={color.label}
    >
      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color.hex }} aria-hidden="true" />
      {pct}% confidence
    </span>
  );
}
