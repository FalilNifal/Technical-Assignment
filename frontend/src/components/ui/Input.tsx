import type { InputHTMLAttributes } from "react";
import { clsx } from "clsx";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> { label?: string; error?: string; }
export function Input({ label, error, className, ...props }: InputProps) {
  return <label className="block"><span className="mb-1.5 block text-sm font-semibold text-slate-700">{label}</span><input className={clsx("h-11 w-full rounded-2xl border border-slate-200 bg-white/90 px-4 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-violet-400 focus:ring-4 focus:ring-violet-100", error && "border-rose-300 focus:ring-rose-100", className)} {...props} />{error && <span className="mt-1.5 block text-xs font-medium text-rose-600">{error}</span>}</label>;
}
