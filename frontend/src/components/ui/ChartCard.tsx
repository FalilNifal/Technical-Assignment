import type { ReactNode } from "react";
import { Card } from "./Card";

interface ChartCardProps { title: string; description?: string; action?: ReactNode; children: ReactNode; className?: string; }
export function ChartCard({ title, description, action, children, className }: ChartCardProps) {
  return <Card className={className}><div className="mb-5 flex flex-col justify-between gap-3 sm:flex-row sm:items-start"><div className="flex items-start gap-3"><span className="mt-1 h-8 w-1.5 shrink-0 rounded-full bg-gradient-to-b from-violet-500 via-fuchsia-500 to-cyan-500" /><div><h2 className="text-lg font-semibold text-slate-950">{title}</h2>{description && <p className="mt-1 text-sm text-slate-500">{description}</p>}</div></div>{action}</div>{children}</Card>;
}
