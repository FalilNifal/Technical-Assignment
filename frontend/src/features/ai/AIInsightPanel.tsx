import { useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Bot, Copy, Sparkles } from "lucide-react";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { getApiErrorMessage } from "../../lib/apiClient";
import { generateTeamInsights, TeamInsightsResponse } from "./ai.api";

function getCurrentWeek() {
  const today = new Date();
  const day = today.getDay();
  const diffToMonday = day === 0 ? -6 : 1 - day;
  const monday = new Date(today);
  monday.setDate(today.getDate() + diffToMonday);
  const sunday = new Date(monday);
  sunday.setDate(monday.getDate() + 6);
  return { week_start: monday.toISOString().slice(0, 10), week_end: sunday.toISOString().slice(0, 10) };
}

function InsightSection({ title, items }: { title: string; items: string[] }) {
  return <div className="rounded-3xl border border-slate-200 bg-white/70 p-4"><h4 className="text-sm font-semibold text-slate-950">{title}</h4>{items.length === 0 ? <p className="mt-2 text-sm text-slate-500">No clear insights found for this section.</p> : <ul className="mt-3 space-y-2">{items.map((item, index) => <li key={index} className="rounded-2xl bg-slate-50 px-3 py-2 text-sm leading-6 text-slate-700 ring-1 ring-slate-100">{item}</li>)}</ul>}</div>;
}

export function AIInsightPanel() {
  const [result, setResult] = useState<TeamInsightsResponse | null>(null);
  const [error, setError] = useState("");
  const week = useMemo(() => getCurrentWeek(), []);
  const mutation = useMutation({
    mutationFn: generateTeamInsights,
    onSuccess: (data) => { setResult(data); setError(""); },
    onError: (err) => setError(getApiErrorMessage(err)),
  });

  function handleGenerate() {
    mutation.mutate({ week_start: week.week_start, week_end: week.week_end, project_id: null, member_id: null });
  }

  function copySummary() {
    if (!result) return;
    const text = `
Summary:
${result.insights.summary}

Achievements:
${result.insights.achievements.map((x) => `- ${x}`).join("\n")}

Blockers:
${result.insights.blockers.map((x) => `- ${x}`).join("\n")}

Risks:
${result.insights.risks.map((x) => `- ${x}`).join("\n")}

Recommendations:
${result.insights.recommendations.map((x) => `- ${x}`).join("\n")}
`.trim();
    navigator.clipboard.writeText(text);
  }

  return <Card className="relative overflow-hidden border-brand-100 bg-gradient-to-br from-white via-brand-50/60 to-accent-50/60"><div className="absolute right-0 top-0 h-32 w-32 rounded-full bg-brand-200/40 blur-3xl" /><div className="relative flex flex-col justify-between gap-4 sm:flex-row sm:items-start"><div className="flex items-start gap-3"><div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-950 text-white shadow-soft"><Bot className="h-6 w-6" /></div><div><div className="flex items-center gap-2"><h2 className="text-lg font-semibold text-slate-950">AI Team Intelligence</h2><Badge value="AI" /></div><p className="mt-1 text-sm leading-6 text-slate-500">Generate manager-ready insights from submitted reports using only allowed report fields.</p></div></div><Button variant="ai" onClick={handleGenerate} isLoading={mutation.isPending}><Sparkles className="h-4 w-4" />Generate insights</Button></div>{error && <div className="relative mt-5 rounded-2xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700 ring-1 ring-red-100">{error}</div>}{mutation.isPending && <div className="relative mt-6 animate-pulse space-y-3"><div className="h-4 w-3/4 rounded-full bg-slate-200" /><div className="h-4 w-full rounded-full bg-slate-200" /><div className="h-4 w-5/6 rounded-full bg-slate-200" /><div className="h-28 rounded-3xl bg-white/70" /></div>}{result && <div className="relative mt-6 space-y-6 animate-slide-up"><div className="flex flex-wrap items-center gap-2">{result.context.generated_by_fallback && <span className="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700 ring-1 ring-amber-200">Fallback summary</span>}<span className="text-xs font-medium text-slate-500">Based on {result.context.reports_used} submitted report(s)</span></div><div><h3 className="text-sm font-semibold text-slate-950">Executive Summary</h3><p className="mt-2 rounded-3xl bg-white/85 p-4 text-sm leading-6 text-slate-700 shadow-sm ring-1 ring-slate-100">{result.insights.summary}</p></div><div className="grid gap-4 lg:grid-cols-2"><InsightSection title="Achievements" items={result.insights.achievements} /><InsightSection title="Blockers" items={result.insights.blockers} /><InsightSection title="Risks" items={result.insights.risks} /><InsightSection title="Recommendations" items={result.insights.recommendations} /></div><div className="flex justify-end"><Button variant="secondary" onClick={copySummary}><Copy className="h-4 w-4" />Copy summary</Button></div></div>}</Card>;
}
