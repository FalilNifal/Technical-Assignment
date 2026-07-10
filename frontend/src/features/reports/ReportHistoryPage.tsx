import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, Pencil } from "lucide-react";
import { AppShell } from "../../components/layout/AppShell";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { DataTable } from "../../components/ui/DataTable";
import { EmptyState } from "../../components/ui/EmptyState";
import { LoadingSkeleton } from "../../components/ui/LoadingSkeleton";
import { formatDate, formatDateTime } from "../../lib/formatters";
import { getMyReports } from "./reports.api";

export function ReportHistoryPage() {
  const query = useQuery({ queryKey: ["my-reports"], queryFn: getMyReports });
  const navigate = useNavigate();
  return <AppShell><div className="space-y-6"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="text-sm font-semibold text-violet-600">Archive</p><h2 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">Report History</h2><p className="mt-2 text-sm leading-6 text-slate-500">Review every weekly report you have created or submitted.</p></div><Button variant="secondary" onClick={() => navigate("/member/dashboard")}><ArrowLeft className="h-4 w-4" />Back to dashboard</Button></div>{query.isLoading && <LoadingSkeleton />}{query.isError && <Card><p className="font-semibold text-red-700">Could not load report history.</p></Card>}{query.data && query.data.reports.length === 0 && <EmptyState title="No reports yet" description="Once you create weekly reports, they will appear here." />}{query.data && query.data.reports.length > 0 && <Card><DataTable><thead className="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-slate-500"><tr><th className="px-5 py-3">Week</th><th className="px-5 py-3">Project</th><th className="px-5 py-3">Status</th><th className="px-5 py-3">Hours</th><th className="px-5 py-3">Submitted</th><th className="px-5 py-3">Updated</th><th className="px-5 py-3">Actions</th></tr></thead><tbody className="divide-y divide-slate-100">{query.data.reports.map((report)=><tr key={report.id} className="transition hover:bg-violet-50/50"><td className="px-5 py-4 text-slate-700">{formatDate(report.week_start)} - {formatDate(report.week_end)}</td><td className="px-5 py-4 font-semibold text-slate-950">{report.project.name}</td><td className="px-5 py-4"><Badge value={report.is_late ? "LATE" : report.status} /></td><td className="px-5 py-4 text-slate-600">{report.hours_worked ?? "-"}</td><td className="px-5 py-4 text-slate-600">{formatDateTime(report.submitted_at)}</td><td className="px-5 py-4 text-slate-600">{formatDateTime(report.updated_at)}</td><td className="px-5 py-4"><Link to={`/member/reports/${report.id}/edit`} className="inline-flex items-center gap-1.5 font-semibold text-violet-600 transition hover:text-violet-700"><Pencil className="h-3.5 w-3.5" />Edit</Link></td></tr>)}</tbody></DataTable></Card>}</div></AppShell>;
}
