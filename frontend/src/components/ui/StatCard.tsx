import type { LucideIcon } from "lucide-react";
import { ArrowUpRight } from "lucide-react";
import { clsx } from "clsx";
import { Card } from "./Card";

interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: LucideIcon;
  tone?: "brand" | "accent" | "success" | "warning" | "danger" | "slate" | "violet" | "pink" | "teal";
  trend?: string;
}

const tones = {
  brand: "from-indigo-500 via-violet-500 to-fuchsia-500 text-white",
  accent: "from-cyan-500 via-sky-500 to-blue-600 text-white",
  success: "from-emerald-400 via-emerald-500 to-teal-500 text-white",
  warning: "from-amber-400 via-orange-500 to-orange-600 text-white",
  danger: "from-rose-500 via-red-500 to-red-600 text-white",
  slate: "from-slate-900 to-slate-700 text-white",
  violet: "from-violet-500 via-purple-500 to-fuchsia-500 text-white",
  pink: "from-fuchsia-500 via-pink-500 to-rose-500 text-white",
  teal: "from-teal-400 via-cyan-500 to-sky-500 text-white",
};

export function StatCard({ title, value, description, icon: Icon, tone = "brand", trend }: StatCardProps) {
  return <Card className="group overflow-hidden p-0 transition hover:-translate-y-1 hover:shadow-panel"><div className={clsx("relative min-h-36 bg-gradient-to-br p-5", tones[tone])}><div className="absolute right-0 top-0 h-24 w-24 rounded-full bg-white/15 blur-2xl" /><div className="relative flex items-start justify-between"><div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/18 ring-1 ring-white/20"><Icon className="h-5 w-5" /></div>{trend && <span className="inline-flex items-center gap-1 rounded-full bg-white/18 px-2.5 py-1 text-xs font-semibold ring-1 ring-white/20"><ArrowUpRight className="h-3.5 w-3.5" />{trend}</span>}</div><div className="relative mt-6"><p className="text-sm font-medium opacity-80">{title}</p><p className="mt-1 text-3xl font-bold tracking-tight">{value}</p>{description && <p className="mt-2 text-xs font-medium opacity-75">{description}</p>}</div></div></Card>;
}
