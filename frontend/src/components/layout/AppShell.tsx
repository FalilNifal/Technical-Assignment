import type { ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

interface AppShellProps { children: ReactNode; }
export function AppShell({ children }: AppShellProps) {
  return <div className="min-h-screen bg-slate-100/80"><div className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(circle_at_20%_0%,rgba(99,102,241,0.18),transparent_32rem),radial-gradient(circle_at_90%_10%,rgba(6,182,212,0.16),transparent_30rem)]" /><div className="flex min-h-screen"><Sidebar /><main className="flex min-h-screen flex-1 flex-col px-4 pb-24 pt-4 sm:px-6 lg:ml-72 lg:px-8 lg:pb-8"><Topbar /><div className="mt-6 flex-1 animate-slide-up">{children}</div></main></div></div>;
}
