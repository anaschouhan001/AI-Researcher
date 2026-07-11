import * as React from "react";
import { cn } from "@/lib/utils";

type ButtonVariant = "default" | "secondary" | "outline" | "ghost" | "destructive";
type ButtonSize = "default" | "sm" | "lg" | "icon";

const variantClasses: Record<ButtonVariant, string> = {
  default:
    "bg-gradient-to-r from-pink-500 via-fuchsia-500 to-rose-400 bg-[length:200%_auto] text-white shadow-candy hover:bg-right hover:shadow-candy-lg",
  secondary: "bg-pink-100 text-pink-700 hover:bg-pink-200 border-2 border-pink-200",
  outline:
    "border-2 border-pink-300 bg-white/60 text-pink-600 hover:bg-pink-100 hover:text-pink-700",
  ghost: "bg-transparent text-pink-500 hover:bg-pink-100 hover:text-pink-700",
  destructive: "bg-rose-500 text-white hover:bg-rose-400 shadow-candy",
};

const sizeClasses: Record<ButtonSize, string> = {
  default: "h-10 px-5 py-2 text-sm",
  sm: "h-8 px-4 text-xs",
  lg: "h-12 px-7 text-base",
  icon: "h-10 w-10",
};

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", type = "button", ...props }, ref) => (
    <button
      ref={ref}
      type={type}
      className={cn(
        "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full font-semibold transition-all duration-300",
        "hover:-translate-y-0.5 active:translate-y-0 active:scale-95",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-pink-400 focus-visible:ring-offset-2 focus-visible:ring-offset-pink-50",
        "disabled:pointer-events-none disabled:opacity-50",
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    />
  )
);
Button.displayName = "Button";

export { Button };
