import * as React from "react";
import { cn } from "@/lib/utils";

type BadgeVariant =
  | "default"
  | "secondary"
  | "outline"
  | "success"
  | "warning"
  | "danger"
  | "info";

const variantClasses: Record<BadgeVariant, string> = {
  default: "border-pink-300/60 bg-pink-100 text-pink-600",
  secondary: "border-pink-200 bg-white/80 text-pink-500",
  outline: "border-pink-300 bg-transparent text-pink-500",
  success: "border-emerald-300/60 bg-emerald-50 text-emerald-600",
  warning: "border-amber-300/60 bg-amber-50 text-amber-600",
  danger: "border-rose-300/60 bg-rose-50 text-rose-600",
  info: "border-fuchsia-300/60 bg-fuchsia-50 text-fuchsia-600",
};

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}

export { Badge };
