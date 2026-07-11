import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge Tailwind class names, resolving conflicts (shadcn convention). */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/** 12345 -> "12.3k", 1200000 -> "1.2M". */
export function formatCompact(value: number): string {
  if (!Number.isFinite(value)) return "—";
  return new Intl.NumberFormat("en", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

/** Best-effort human date. Returns the raw string when unparsable. */
export function formatDate(value: string | undefined | null): string {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/**
 * Normalize a confidence value that may arrive as a 0-1 fraction or a 0-100
 * percentage into a clamped 0-100 integer.
 */
export function normalizeConfidence(value: number): number {
  const pct = value <= 1 ? value * 100 : value;
  return Math.round(Math.min(100, Math.max(0, pct)));
}

/** Color-code a 0-100 confidence percentage. */
export function confidenceColor(pct: number): {
  hex: string;
  text: string;
  bg: string;
  label: string;
} {
  if (pct >= 85) {
    return {
      hex: "#0ca30c",
      text: "text-emerald-600",
      bg: "bg-emerald-50 border-emerald-300",
      label: "High confidence",
    };
  }
  if (pct >= 60) {
    return {
      hex: "#d97706",
      text: "text-amber-600",
      bg: "bg-amber-50 border-amber-300",
      label: "Moderate confidence",
    };
  }
  return {
    hex: "#d03b3b",
    text: "text-rose-600",
    bg: "bg-rose-50 border-rose-300",
    label: "Low confidence",
  };
}

export function truncate(text: string, max: number): string {
  if (text.length <= max) return text;
  return `${text.slice(0, max - 1).trimEnd()}…`;
}
