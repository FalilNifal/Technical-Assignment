import type { ReactNode } from "react";
import { Inbox } from "lucide-react";
import { Card } from "./Card";

interface EmptyStateProps { title: string; description?: string; action?: ReactNode; }
export function EmptyState({ title, description, action }: EmptyStateProps) {
  return <Card className="flex flex-col items-center justify-center px-6 py-12 text-center"><div className="mb-4 flex h-14 w-14 items-center justify-center rounded-3xl bg-gradient-to-br from-violet-500 via-fuchsia-500 to-cyan-500 text-white shadow-glow-violet"><Inbox className="h-6 w-6" /></div><h3 className="text-base font-semibold text-slate-950">{title}</h3>{description && <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">{description}</p>}{action && <div className="mt-6">{action}</div>}</Card>;
}
