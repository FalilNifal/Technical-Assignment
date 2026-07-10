import { clsx } from "clsx";
import type { ReportStatus, Role } from "../../types";

type BadgeType = ReportStatus | Role | "BLOCKED" | "AI";
interface BadgeProps { value: BadgeType | string; }
const styles: Record<string, string> = {
  SUBMITTED: "bg-gradient-to-r from-emerald-500 to-teal-500 text-white ring-emerald-300/50 shadow-sm",
  DRAFT: "bg-slate-100 text-slate-700 ring-slate-200",
  PENDING: "bg-gradient-to-r from-amber-400 to-orange-500 text-white ring-amber-300/50 shadow-sm",
  LATE: "bg-gradient-to-r from-rose-500 to-red-500 text-white ring-rose-300/50 shadow-sm",
  ARCHIVED: "bg-zinc-100 text-zinc-600 ring-zinc-200",
  BLOCKED: "bg-gradient-to-r from-rose-500 to-red-500 text-white ring-rose-300/50 shadow-sm",
  TEAM_MEMBER: "bg-gradient-to-r from-cyan-500 to-sky-500 text-white ring-cyan-300/50 shadow-sm",
  MANAGER: "bg-gradient-to-r from-indigo-500 to-violet-500 text-white ring-indigo-300/50 shadow-sm",
  ADMIN: "bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white ring-violet-300/50 shadow-sm",
  AI: "bg-gradient-to-r from-violet-500 via-fuchsia-500 to-cyan-500 text-white ring-fuchsia-300/50 shadow-sm",
};
export function Badge({ value }: BadgeProps) {
  return <span className={clsx("inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset", styles[value] || "bg-slate-100 text-slate-700 ring-slate-200")}>{String(value).replace("_", " ")}</span>;
}
