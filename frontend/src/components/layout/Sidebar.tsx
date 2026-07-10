import { useState } from "react";
import { BarChart3, FilePlus2, FolderKanban, History, Home, LogOut, Sparkles, Users2, type LucideIcon } from "lucide-react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { clsx } from "clsx";
import { authStorage } from "../../lib/auth";

type NavItem = { label: string; icon: LucideIcon; to?: string; section?: string };

const memberLinks: NavItem[] = [
  { label: "Overview", to: "/member/dashboard", icon: Home },
  { label: "New Report", to: "/member/reports/new", icon: FilePlus2 },
  { label: "History", to: "/member/reports/history", icon: History },
];
// Manager links scroll to sections that live on the single dashboard page.
const managerLinks: NavItem[] = [
  { label: "Overview", section: "top", icon: BarChart3 },
  { label: "Team", section: "team", icon: Users2 },
  { label: "Insights", section: "insights", icon: Sparkles },
  { label: "Projects", to: "/manager/projects", icon: FolderKanban },
];

function BrandMark() {
  return <div className="flex items-center gap-3"><div className="relative flex h-11 w-11 items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-br from-violet-600 via-fuchsia-500 to-cyan-500 shadow-glow-violet"><div className="absolute h-5 w-5 -translate-x-1 rounded-full bg-white/80" /><div className="absolute h-5 w-5 translate-x-1 rounded-full bg-cyan-200 mix-blend-screen" /></div><div><p className="text-lg font-bold tracking-tight text-slate-950">PulseBoard</p><p className="text-xs font-medium text-slate-500">Team intelligence</p></div></div>;
}

function SidebarLink({ link, mobile, active, onSection }: { link: NavItem; mobile?: boolean; active?: boolean; onSection: (section: string) => void }) {
  const Icon = link.icon;
  const base = mobile
    ? "flex flex-col items-center gap-1 rounded-2xl px-2 py-2 text-[11px] font-semibold transition"
    : "group flex w-full items-center gap-3 rounded-2xl px-3 py-3 text-sm font-semibold transition-all";
  const activeCls = mobile
    ? "bg-gradient-to-r from-violet-600 to-fuchsia-500 text-white"
    : "bg-gradient-to-r from-violet-600 via-fuchsia-500 to-cyan-500 text-white shadow-glow-violet";
  const inactiveCls = mobile ? "text-slate-500" : "text-slate-500 hover:bg-violet-50 hover:text-violet-700";
  const iconCls = mobile ? "h-4 w-4" : "h-5 w-5";

  if (link.section) {
    return <button type="button" onClick={() => onSection(link.section!)} className={clsx(base, active ? activeCls : inactiveCls)}><Icon className={iconCls} /><span>{link.label}</span></button>;
  }
  return <NavLink to={link.to!} className={({ isActive }) => clsx(base, isActive ? activeCls : inactiveCls)}><Icon className={iconCls} /><span>{link.label}</span></NavLink>;
}

export function Sidebar() {
  const user = authStorage.getUser();
  const navigate = useNavigate();
  const links = user?.role === "TEAM_MEMBER" ? memberLinks : managerLinks;
  const location = useLocation();
  const [activeSection, setActiveSection] = useState("top");

  function logout() { authStorage.clear(); navigate("/login"); }
  function goToSection(section: string) {
    setActiveSection(section);
    // Section anchors live on the manager dashboard; if we're elsewhere, go there first.
    if (!location.pathname.startsWith("/manager/dashboard")) {
      navigate("/manager/dashboard");
      return;
    }
    if (section === "top") { window.scrollTo({ top: 0, behavior: "smooth" }); return; }
    document.getElementById(section)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  return <><aside className="fixed inset-y-4 left-4 z-30 hidden w-64 flex-col rounded-4xl border border-white/70 bg-white/75 p-4 shadow-panel ring-1 ring-slate-900/5 backdrop-blur-xl lg:flex"><BrandMark /><div className="mt-8"><p className="mb-3 px-3 text-xs font-bold uppercase tracking-[0.18em] text-slate-400">Workspace</p><nav className="space-y-1">{links.map((link) => <SidebarLink key={link.label} link={link} active={activeSection === link.section} onSection={goToSection} />)}</nav></div><div className="mt-auto space-y-4"><div className="rounded-3xl border border-violet-100 bg-gradient-to-br from-violet-50 via-fuchsia-50 to-cyan-50 p-4"><p className="text-xs font-semibold uppercase tracking-wide text-violet-600">Signed in as</p><p className="mt-2 truncate text-sm font-bold text-slate-950">{user?.full_name ?? "Pulse User"}</p><p className="truncate text-xs text-slate-500">{user?.email ?? "team@pulseboard.app"}</p></div><button onClick={logout} className="flex w-full items-center gap-3 rounded-2xl px-3 py-3 text-sm font-semibold text-slate-500 transition hover:bg-rose-50 hover:text-rose-600"><LogOut className="h-5 w-5" />Logout</button></div></aside><nav className="fixed inset-x-3 bottom-3 z-40 grid grid-cols-3 gap-2 rounded-3xl border border-white/70 bg-white/85 p-2 shadow-panel backdrop-blur-xl lg:hidden">{links.slice(0, 3).map((link) => <SidebarLink key={`mobile-${link.label}`} link={link} mobile active={activeSection === link.section} onSection={goToSection} />)}</nav></>;
}
