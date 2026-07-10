import type { ButtonHTMLAttributes, ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { clsx } from "clsx";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger" | "ai" | "success" | "sunset";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
}

const baseStyles = "inline-flex shrink-0 items-center justify-center gap-2 rounded-2xl font-semibold tracking-normal transition-all duration-200 focus:outline-none focus:ring-4 disabled:pointer-events-none disabled:opacity-60";
const variants: Record<ButtonVariant, string> = {
  primary: "bg-gradient-to-r from-brand-600 via-violet-600 to-fuchsia-500 text-white shadow-glow-violet hover:-translate-y-0.5 hover:brightness-110 active:translate-y-0 focus:ring-violet-200",
  secondary: "border border-slate-200 bg-white/90 text-slate-700 shadow-sm hover:-translate-y-0.5 hover:border-violet-300 hover:bg-violet-50 hover:text-violet-700 active:translate-y-0 focus:ring-violet-100",
  ghost: "bg-transparent text-slate-500 hover:bg-white/80 hover:text-violet-700 focus:ring-violet-100",
  danger: "bg-gradient-to-r from-rose-500 to-red-600 text-white shadow-glow-rose hover:-translate-y-0.5 hover:brightness-110 active:translate-y-0 focus:ring-rose-200",
  success: "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-glow-teal hover:-translate-y-0.5 hover:brightness-110 active:translate-y-0 focus:ring-emerald-200",
  sunset: "bg-gradient-to-r from-amber-400 via-orange-500 to-rose-500 text-white shadow-glow-amber hover:-translate-y-0.5 hover:brightness-110 active:translate-y-0 focus:ring-orange-200",
  ai: "bg-gradient-to-r from-violet-600 via-fuchsia-500 to-cyan-500 bg-[length:200%_auto] text-white shadow-glow-pink hover:-translate-y-0.5 hover:animate-sheen active:translate-y-0 focus:ring-fuchsia-200",
};
const sizes: Record<ButtonSize, string> = {
  sm: "h-9 px-3 text-xs",
  md: "h-11 px-4 text-sm",
  lg: "h-12 px-6 text-base",
};

export function Button({ children, className, variant = "primary", size = "md", isLoading = false, disabled, ...props }: ButtonProps) {
  return <button className={clsx(baseStyles, variants[variant], sizes[size], className)} disabled={disabled || isLoading} {...props}>{isLoading && <Loader2 className="h-4 w-4 animate-spin" />}<span className="inline-flex items-center gap-2">{isLoading ? "Loading" : children}</span></button>;
}
