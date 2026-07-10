import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CalendarDays, Clock3, FileText, Pencil, PlusCircle, Send } from "lucide-react";
import { AppShell } from "../../components/layout/AppShell";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { ChartCard } from "../../components/ui/ChartCard";
import { EmptyState } from "../../components/ui/EmptyState";
import { LoadingSkeleton } from "../../components/ui/LoadingSkeleton";
import { StatCard } from "../../components/ui/StatCard";
import { formatDate } from "../../lib/formatters";
import { getCurrentWeekReports } from "./reports.api";

export function MemberDashboardPage() {
  const query = useQuery({ queryKey: ["current-week-reports"], queryFn: getCurrentWeekReports });
  const reports = query.data?.reports ?? [];
  const submitted = reports.filter((report) => report.status === "SUBMITTED").length;
  const drafts = reports.filter((report) => report.status === "DRAFT").length;
  const late = reports.filter((report) => report.is_late).length;
  const trend = reports.length
    ? reports.map((report, index) => ({ name: report.project.name, hours: Number(report.hours_worked ?? 0), progress: (index + 1) * 12 + 24 }))
    : [{ name: "Plan", hours: 4, progress: 25 }, { name: "Build", hours: 8, progress: 55 }, { name: "Review", hours: 6, progress: 72 }, { name: "Ship", hours: 10, progress: 90 }];

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Hero */}
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <p className="text-sm font-semibold text-violet-600">Member workspace</p>
            <h2 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">
              My Weekly <span className="text-aurora">Reports</span>
            </h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
              Create, submit, and review structured updates with a colorful, polished workflow.
            </p>
          </div>
          <Link to="/member/reports/new">
            <Button size="lg" variant="ai"><PlusCircle className="h-4 w-4" />Create report</Button>
          </Link>
        </div>

        {query.isLoading && <LoadingSkeleton />}
        {query.isError && (
          <Card>
            <p className="font-semibold text-rose-700">Could not load your reports.</p>
            <p className="mt-1 text-sm text-slate-500">Please refresh and try again.</p>
          </Card>
        )}

        {query.data && (
          <>
            {/* Stat cards */}
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard title="Current Week" value={`${formatDate(query.data.week_start).slice(0, 6)} - ${formatDate(query.data.week_end).slice(0, 6)}`} description="Active reporting period" icon={CalendarDays} tone="violet" />
              <StatCard title="Reports" value={reports.length} description="Created this week" icon={FileText} tone="teal" />
              <StatCard title="Submitted" value={submitted} description={`${drafts} draft report(s)`} icon={Send} tone="success" />
              <StatCard title="Late" value={late} description="After deadline" icon={Clock3} tone="pink" />
            </div>

            {/* Progress + current reports */}
            <div className="grid gap-6 xl:grid-cols-[.9fr_1.1fr]">
              <ChartCard title="Weekly Progress" description="A visual snapshot of your submitted work and hours.">
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={trend}>
                      <defs>
                        <linearGradient id="memberProgress" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.38} />
                          <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ede9fe" />
                      <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
                      <YAxis tickLine={false} axisLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
                      <Tooltip contentStyle={{ borderRadius: 16, border: "1px solid #ede9fe" }} />
                      <Area type="monotone" dataKey="hours" stroke="#8b5cf6" fill="url(#memberProgress)" strokeWidth={3} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </ChartCard>

              <Card>
                <div className="mb-5 flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-950">Current Reports</h3>
                    <p className="mt-1 text-sm text-slate-500">Report cards for the active week.</p>
                  </div>
                  <Badge value={submitted ? "SUBMITTED" : "DRAFT"} />
                </div>
                {reports.length === 0 ? (
                  <EmptyState
                    title="No report created for this week"
                    description="Create your weekly report to keep your manager updated on progress, blockers, and next week's plan."
                    action={<Link to="/member/reports/new"><Button variant="ai">Create report</Button></Link>}
                  />
                ) : (
                  <div className="grid gap-4 md:grid-cols-2">
                    {reports.map((report) => (
                      <div key={report.id} className="relative overflow-hidden rounded-3xl border border-violet-100 bg-gradient-to-br from-white to-violet-50/50 p-5 transition hover:-translate-y-1 hover:shadow-glow-violet">
                        <span className="absolute inset-y-0 left-0 w-1.5 bg-gradient-to-b from-violet-500 via-fuchsia-500 to-cyan-500" />
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="font-semibold text-slate-950">{report.project.name}</p>
                            <p className="mt-1 text-xs text-slate-500">Updated {formatDate(report.updated_at)}</p>
                          </div>
                          <Badge value={report.is_late ? "LATE" : report.status} />
                        </div>
                        <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-600">{report.tasks_completed || "No completed tasks added yet."}</p>
                        <Link to={`/member/reports/${report.id}/edit`} className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-violet-600 transition hover:text-violet-700"><Pencil className="h-3.5 w-3.5" />Edit report</Link>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
