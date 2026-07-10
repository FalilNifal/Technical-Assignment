import { Bell, Command, LogOut, Search, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { authStorage } from "../../lib/auth";

export function Topbar() {
  const user = authStorage.getUser();
  const navigate = useNavigate();
  const firstName = user?.full_name?.split(" ")[0] ?? "there";
  function logout() { authStorage.clear(); navigate("/login"); }
  return <header className="sticky top-4 z-20 rounded-3xl border border-white/70 bg-white/75 px-4 py-3 shadow-soft ring-1 ring-slate-900/5 backdrop-blur-xl"><div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-violet-600">PulseBoard</p><h1 className="mt-1 text-xl font-bold tracking-tight text-slate-950 sm:text-2xl">Good evening, <span className="text-aurora">{firstName}</span></h1></div><div className="flex items-center gap-2 sm:gap-3"><div className="hidden h-11 w-72 items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-3 text-sm text-slate-400 md:flex"><Search className="h-4 w-4" /><span className="flex-1">Search reports, projects...</span><kbd className="rounded-lg bg-white px-2 py-1 text-[10px] font-bold text-slate-400 shadow-sm"><Command className="inline h-3 w-3" />K</kbd></div><Button variant="ai" className="hidden sm:inline-flex"><Sparkles className="h-4 w-4" />Upgrade</Button><button className="flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-600 shadow-sm transition hover:border-violet-300 hover:text-violet-600" aria-label="Notifications"><Bell className="h-5 w-5" /></button>{user && <Badge value={user.role} />}<button type="button" onClick={logout} aria-label="Logout" className="flex h-11 items-center gap-2 rounded-2xl border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-600 shadow-sm transition hover:border-rose-200 hover:bg-rose-50 hover:text-rose-600"><LogOut className="h-4 w-4" /><span className="hidden sm:inline">Logout</span></button></div></div></header>;
}
