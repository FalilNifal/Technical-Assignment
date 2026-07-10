import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { AlertTriangle, Bell, CheckCircle2, ClipboardList, Clock, FileText, Filter, RefreshCw, RotateCcw, Users2, X } from "lucide-react";
import { AppShell } from "../../components/layout/AppShell";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { ChartCard } from "../../components/ui/ChartCard";
import { DataTable } from "../../components/ui/DataTable";
import { EmptyState } from "../../components/ui/EmptyState";
import { LoadingSkeleton } from "../../components/ui/LoadingSkeleton";
import { StatCard } from "../../components/ui/StatCard";
import { formatDate, formatDateTime, formatNumber } from "../../lib/formatters";
import { AIInsightPanel } from "../ai/AIInsightPanel";
import { ChatWidget } from "../ai/ChatWidget";
import { getProjects } from "../reports/reports.api";
import { getActivityTimeline, getDashboardSummary, getProjectDistribution, getTeamMembers, getTeamPerformance, getTeamReports } from "./dashboard.api";
import type { ActivityTimelineItem } from "../../types";

const DASHBOARD_REFETCH_MS = 30000;
const ACTIVITY_REFETCH_MS = 15000;
const COLORS = ["#8b5cf6", "#ec4899", "#06b6d4", "#f59e0b", "#10b981", "#3b82f6"];

function activityKey(activity: ActivityTimelineItem | undefined) {
  return activity ? `${activity.id}:${activity.type}:${activity.created_at}` : "";
}

// Snap any picked day to its Monday so filtering aligns with stored Mon–Sun weeks.
function mondayOf(iso: string): string {
  const d = new Date(`${iso}T00:00:00`);
  const day = d.getDay();
  d.setDate(d.getDate() + (day === 0 ? -6 : 1 - day));
  return d.toISOString().slice(0, 10);
}
function addDays(iso: string, n: number): string {
  const d = new Date(`${iso}T00:00:00`);
  d.setDate(d.getDate() + n);
  return d.toISOString().slice(0, 10);
}

export function ManagerDashboardPage() {
  const queryClient = useQueryClient();
  const [notification, setNotification] = useState<ActivityTimelineItem | null>(null);
  const latestSeenActivity = useRef("");
  const hasLoadedActivity = useRef(false);

  const [filters, setFilters] = useState({ weekStart: "", projectId: "", memberId: "" });
  const hasFilters = Boolean(filters.weekStart || filters.projectId || filters.memberId);

  const apiFilters = useMemo(() => {
    const monday = filters.weekStart ? mondayOf(filters.weekStart) : "";
    return {
      week_start: monday || undefined,
      week_end: monday ? addDays(monday, 6) : undefined,
      project_id: filters.projectId || undefined,
      member_id: filters.memberId || undefined,
    };
  }, [filters]);

  const projectsList = useQuery({ queryKey: ["projects-list"], queryFn: getProjects });
  const membersList = useQuery({ queryKey: ["members-list"], queryFn: getTeamMembers });

  const summaryQuery = useQuery({ queryKey: ["dashboard-summary", apiFilters], queryFn: () => getDashboardSummary(apiFilters), refetchInterval: DASHBOARD_REFETCH_MS });
  const projectQuery = useQuery({ queryKey: ["project-distribution", apiFilters], queryFn: () => getProjectDistribution(apiFilters), refetchInterval: DASHBOARD_REFETCH_MS });
  const teamQuery = useQuery({ queryKey: ["team-performance", apiFilters], queryFn: () => getTeamPerformance(apiFilters), refetchInterval: DASHBOARD_REFETCH_MS });
  const activityQuery = useQuery({ queryKey: ["activity-timeline", apiFilters], queryFn: () => getActivityTimeline(apiFilters), refetchInterval: ACTIVITY_REFETCH_MS });
  const reportsQuery = useQuery({ queryKey: ["team-reports", apiFilters], queryFn: () => getTeamReports(apiFilters) });

  const latestActivity = useMemo(() => activityQuery.data?.items[0], [activityQuery.data]);
  const summary = summaryQuery.data;
  const projectItems = projectQuery.data?.items ?? [];
  const teamItems = teamQuery.data?.items ?? [];
  const reportItems = reportsQuery.data?.items ?? [];

  const projectChartData = useMemo(() => projectItems.map((item) => ({
    name: item.project_name,
    hours: Number(item.total_hours ?? 0),
    reports: item.report_count,
    blockers: item.blocker_count,
  })), [projectItems]);

  const trendData = useMemo(() => {
    const source = projectChartData.length ? projectChartData : [
      { name: "Mon", hours: 18, reports: 4, blockers: 1 },
      { name: "Tue", hours: 26, reports: 6, blockers: 2 },
      { name: "Wed", hours: 22, reports: 5, blockers: 1 },
      { name: "Thu", hours: 34, reports: 8, blockers: 3 },
      { name: "Fri", hours: 29, reports: 7, blockers: 2 },
    ];
    return source.slice(0, 7);
  }, [projectChartData]);

  const donutData = summary ? [
    { name: "Submitted", value: summary.submitted_reports },
    { name: "Draft", value: summary.draft_reports },
    { name: "Late", value: summary.late_reports },
    { name: "Pending", value: summary.pending_members },
  ] : [];

  useEffect(() => {
    const key = activityKey(latestActivity);
    if (!key) return;
    if (!hasLoadedActivity.current) {
      latestSeenActivity.current = key;
      hasLoadedActivity.current = true;
      return;
    }
    if (key !== latestSeenActivity.current) {
      latestSeenActivity.current = key;
      setNotification(latestActivity ?? null);
    }
  }, [latestActivity]);

  function refreshDashboard() {
    void queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    void queryClient.invalidateQueries({ queryKey: ["project-distribution"] });
    void queryClient.invalidateQueries({ queryKey: ["team-performance"] });
    void queryClient.invalidateQueries({ queryKey: ["activity-timeline"] });
    void queryClient.invalidateQueries({ queryKey: ["team-reports"] });
    setNotification(null);
  }

  function resetFilters() {
    setFilters({ weekStart: "", projectId: "", memberId: "" });
  }

  const isLoading = summaryQuery.isLoading || projectQuery.isLoading || teamQuery.isLoading || activityQuery.isLoading;

  return (
    <AppShell>
      <div className="space-y-6">
        {notification && (
          <Card className="border-violet-200 bg-gradient-to-r from-violet-50 via-fuchsia-50 to-cyan-50">
            <div className="flex items-start justify-between gap-4">
              <div className="flex gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 to-fuchsia-500 text-white shadow-glow-violet">
                  <Bell className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-950">New report activity</p>
                  <p className="mt-1 text-sm text-slate-600">{notification.description}</p>
                  <p className="mt-1 text-xs text-slate-500">{formatDateTime(notification.created_at)}</p>
                </div>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <Button size="sm" onClick={refreshDashboard}>Refresh</Button>
                <button type="button" className="rounded-xl p-2 text-slate-400 transition hover:bg-white hover:text-slate-950" onClick={() => setNotification(null)} aria-label="Dismiss notification">
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          </Card>
        )}

        {isLoading && <LoadingSkeleton />}

        {summaryQuery.isError && (
          <Card>
            <p className="font-semibold text-rose-700">Could not load dashboard analytics.</p>
            <p className="mt-1 text-sm text-slate-500">Check your manager account and API server.</p>
          </Card>
        )}

        {summary && (
          <>
            {/* Hero */}
            <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-end">
              <div>
                <p className="text-sm font-semibold text-violet-600">Executive overview</p>
                <h2 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">
                  Manager <span className="text-aurora">Dashboard</span>
                </h2>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                  Track reports, blockers, workload, and team submission health from one vibrant analytics workspace.
                </p>
              </div>
              <Button variant="ai" onClick={refreshDashboard}>
                <RefreshCw className="h-4 w-4" />Refresh data
              </Button>
            </div>

            {/* Filter bar */}
            <Card className="p-4">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-end">
                <div className="flex items-center gap-2 pb-2 text-sm font-semibold text-violet-700 lg:pb-2.5">
                  <Filter className="h-4 w-4" />Filters
                </div>
                <div className="grid flex-1 gap-3 sm:grid-cols-3">
                  <label className="block">
                    <span className="mb-1 block text-xs font-semibold text-slate-500">Week</span>
                    <input type="date" value={filters.weekStart} onChange={(e) => setFilters((f) => ({ ...f, weekStart: e.target.value }))} className="h-10 w-full rounded-2xl border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition focus:border-violet-400 focus:ring-4 focus:ring-violet-100" />
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-xs font-semibold text-slate-500">Project</span>
                    <select value={filters.projectId} onChange={(e) => setFilters((f) => ({ ...f, projectId: e.target.value }))} className="h-10 w-full rounded-2xl border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition focus:border-violet-400 focus:ring-4 focus:ring-violet-100">
                      <option value="">All projects</option>
                      {projectsList.data?.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-1 block text-xs font-semibold text-slate-500">Team member</span>
                    <select value={filters.memberId} onChange={(e) => setFilters((f) => ({ ...f, memberId: e.target.value }))} className="h-10 w-full rounded-2xl border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition focus:border-violet-400 focus:ring-4 focus:ring-violet-100">
                      <option value="">All members</option>
                      {membersList.data?.items.map((m) => <option key={m.member_id} value={m.member_id}>{m.member_name}</option>)}
                    </select>
                  </label>
                </div>
                {hasFilters && <Button variant="secondary" onClick={resetFilters}><RotateCcw className="h-4 w-4" />Reset</Button>}
              </div>
            </Card>

            {/* Stat cards */}
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard title="Total Reports" value={formatNumber(summary.total_reports)} description={`${summary.submitted_reports} submitted this week`} icon={FileText} tone="violet" trend={`${summary.submission_percentage}%`} />
              <StatCard title="Submission Rate" value={`${summary.submission_percentage}%`} description={`${summary.pending_members} member(s) pending`} icon={CheckCircle2} tone="teal" trend="Live" />
              <StatCard title="Open Blockers" value={formatNumber(summary.blocker_count)} description="Risks raised by members" icon={AlertTriangle} tone="warning" />
              <StatCard title="Late Reports" value={formatNumber(summary.late_reports)} description="Needs manager follow-up" icon={Clock} tone="pink" />
            </div>

            {/* Charts row */}
            <div className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
              <ChartCard title="Workload by Project" description="Reported hours, submitted reports, and blocker density." action={<Badge value="AI" />}>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={projectChartData.length ? projectChartData : trendData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ede9fe" />
                      <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
                      <YAxis tickLine={false} axisLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
                      <Tooltip cursor={{ fill: "rgba(139,92,246,0.08)" }} contentStyle={{ borderRadius: 16, border: "1px solid #ede9fe" }} />
                      <Bar dataKey="hours" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
                      <Bar dataKey="reports" fill="#ec4899" radius={[8, 8, 0, 0]} />
                      <Bar dataKey="blockers" fill="#06b6d4" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </ChartCard>

              <ChartCard title="Submission Mix" description="Current weekly reporting distribution.">
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={donutData} dataKey="value" nameKey="name" innerRadius={72} outerRadius={106} paddingAngle={5}>
                        {donutData.map((entry, index) => <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />)}
                      </Pie>
                      <Tooltip contentStyle={{ borderRadius: 16, border: "1px solid #ede9fe" }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {donutData.map((item, index) => (
                    <div key={item.name} className="rounded-2xl bg-gradient-to-br from-slate-50 to-violet-50/60 p-3 ring-1 ring-violet-100/60">
                      <div className="mb-2 h-2 w-8 rounded-full" style={{ background: COLORS[index % COLORS.length] }} />
                      <p className="text-xs text-slate-500">{item.name}</p>
                      <p className="text-lg font-bold text-slate-950">{item.value}</p>
                    </div>
                  ))}
                </div>
              </ChartCard>
            </div>

            {/* Team performance — full width */}
            <section id="team" className="scroll-mt-28">
            <Card>
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-slate-950">Team Performance</h2>
                  <p className="mt-1 text-sm text-slate-500">Submission status and workload per member.</p>
                </div>
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white shadow-glow-violet">
                  <Users2 className="h-5 w-5" />
                </div>
              </div>
              {teamItems.length ? (
                <DataTable>
                  <thead className="bg-gradient-to-r from-violet-50 via-fuchsia-50 to-cyan-50 text-xs font-semibold uppercase tracking-wide text-slate-600">
                    <tr>
                      <th className="px-5 py-3">Member</th>
                      <th className="px-5 py-3">Status</th>
                      <th className="px-5 py-3">Reports</th>
                      <th className="px-5 py-3">Blockers</th>
                      <th className="px-5 py-3">Hours</th>
                      <th className="px-5 py-3">Last submitted</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {teamItems.map((member) => (
                      <tr key={member.member_id} className="transition hover:bg-violet-50/50">
                        <td className="px-5 py-4">
                          <p className="font-semibold text-slate-950">{member.member_name}</p>
                          <p className="text-xs text-slate-500">{member.member_email}</p>
                        </td>
                        <td className="px-5 py-4"><Badge value={member.submission_status} /></td>
                        <td className="px-5 py-4 text-slate-600">{member.report_count}</td>
                        <td className="px-5 py-4 text-slate-600">{member.blocker_count}</td>
                        <td className="px-5 py-4 text-slate-600">{formatNumber(member.total_hours)}</td>
                        <td className="px-5 py-4 text-slate-600">{formatDateTime(member.last_submitted_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </DataTable>
              ) : (
                <EmptyState title="No team data" description="Team performance appears after reports are created." />
              )}
            </Card>
            </section>

            {/* Team reports — raw reports for the selected filters */}
            <section id="reports" className="scroll-mt-28">
              <Card>
                <div className="mb-5 flex items-center justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-950">Team Reports</h2>
                    <p className="mt-1 text-sm text-slate-500">
                      {reportItems.length} report(s){hasFilters ? " matching filters" : " this week"} · {filters.weekStart ? `week of ${mondayOf(filters.weekStart)}` : "current week"}
                    </p>
                  </div>
                  <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 text-white shadow-sm">
                    <ClipboardList className="h-5 w-5" />
                  </div>
                </div>
                {reportsQuery.isLoading ? (
                  <LoadingSkeleton />
                ) : reportItems.length === 0 ? (
                  <EmptyState title="No reports found" description="No reports match the selected week, project, or member." />
                ) : (
                  <div className="grid gap-4 md:grid-cols-2">
                    {reportItems.map((report) => (
                      <article key={report.report_id} className="rounded-3xl border border-slate-200 bg-white p-5 transition hover:border-violet-200 hover:shadow-soft">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="font-semibold text-slate-950">{report.member_name}</p>
                            <p className="mt-0.5 text-xs text-slate-500">{report.project_name} · {formatDate(report.week_start)} – {formatDate(report.week_end)}</p>
                          </div>
                          <Badge value={report.is_late ? "LATE" : report.status} />
                        </div>
                        <div className="mt-4 space-y-3 text-sm">
                          <div>
                            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Completed</p>
                            <p className="mt-1 leading-6 text-slate-700">{report.tasks_completed || "—"}</p>
                          </div>
                          <div>
                            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Planned next</p>
                            <p className="mt-1 leading-6 text-slate-700">{report.tasks_planned || "—"}</p>
                          </div>
                          {report.blockers && report.blockers.trim() && (
                            <div className="rounded-2xl bg-rose-50 px-3 py-2 ring-1 ring-rose-100">
                              <p className="text-xs font-semibold uppercase tracking-wide text-rose-500">Blocker</p>
                              <p className="mt-1 leading-6 text-rose-700">{report.blockers}</p>
                            </div>
                          )}
                        </div>
                        <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
                          <span>{report.hours_worked ? `${report.hours_worked} hrs` : "Hours n/a"}</span>
                          {report.submitted_at && <span>Submitted {formatDateTime(report.submitted_at)}</span>}
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </Card>
            </section>

            {/* Momentum + AI insights */}
            <div className="grid gap-6 xl:grid-cols-2">
              <ChartCard title="Weekly Momentum" description="A clean trend view for report volume and hours.">
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trendData}>
                      <defs>
                        <linearGradient id="hoursGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#a855f7" stopOpacity={0.4} />
                          <stop offset="95%" stopColor="#ec4899" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ede9fe" />
                      <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
                      <YAxis tickLine={false} axisLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
                      <Tooltip contentStyle={{ borderRadius: 16, border: "1px solid #ede9fe" }} />
                      <Area type="monotone" dataKey="hours" stroke="#a855f7" fill="url(#hoursGradient)" strokeWidth={3} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </ChartCard>

              <div id="insights" className="scroll-mt-28">
                <AIInsightPanel />
              </div>
            </div>

            {/* Activity timeline — full width */}
            <Card>
              <h2 className="text-lg font-semibold text-slate-950">Activity Timeline</h2>
              <p className="mt-1 text-sm text-slate-500">Recent submissions, updates, and report changes.</p>
              <div className="mt-6 space-y-5">
                {activityQuery.data?.items.length ? activityQuery.data.items.slice(0, 6).map((activity) => (
                  <div key={`${activity.id}-${activity.type}-${activity.created_at}`} className="relative pl-6 before:absolute before:left-0 before:top-1 before:h-3 before:w-3 before:rounded-full before:bg-gradient-to-br before:from-violet-500 before:to-fuchsia-500 after:absolute after:left-[5px] after:top-5 after:h-full after:w-px after:bg-violet-100 last:after:hidden">
                    <p className="text-sm font-semibold text-slate-950">{activity.title}</p>
                    <p className="mt-1 text-sm leading-6 text-slate-500">{activity.description}</p>
                    <p className="mt-1 text-xs text-slate-400">{formatDateTime(activity.created_at)}</p>
                  </div>
                )) : (
                  <EmptyState title="No activity yet" description="Recent submissions and updates will appear here." />
                )}
              </div>
            </Card>
          </>
        )}
      </div>
      <ChatWidget />
    </AppShell>
  );
}
