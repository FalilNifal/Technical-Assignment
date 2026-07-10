import type { TextareaHTMLAttributes } from "react";
import { clsx } from "clsx";

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> { label?: string; error?: string; }
export function Textarea({ label, error, className, ...props }: TextareaProps) {
  return <label className="block"><span className="mb-1.5 block text-sm font-semibold text-slate-700">{label}</span><textarea className={clsx("min-h-32 w-full resize-y rounded-2xl border border-slate-200 bg-white/90 px-4 py-3 text-sm leading-6 text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-violet-400 focus:ring-4 focus:ring-violet-100", error && "border-rose-300 focus:ring-rose-100", className)} {...props} />{error && <span className="mt-1.5 block text-xs font-medium text-rose-600">{error}</span>}</label>;
}
