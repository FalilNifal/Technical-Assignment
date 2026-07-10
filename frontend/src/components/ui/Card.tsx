import type { ReactNode } from "react";
import { clsx } from "clsx";

interface CardProps { children: ReactNode; className?: string; }
export function Card({ children, className }: CardProps) {
  return <div className={clsx("rounded-3xl border border-white/70 bg-white/85 p-6 shadow-soft shadow-slate-200/70 ring-1 ring-slate-900/5 backdrop-blur-xl transition-shadow duration-300 hover:shadow-panel animate-fade-in", className)}>{children}</div>;
}
