import { useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Save, Send } from "lucide-react";
import { AppShell } from "../../components/layout/AppShell";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { LoadingSkeleton } from "../../components/ui/LoadingSkeleton";
import { Textarea } from "../../components/ui/Textarea";
import { getApiErrorMessage } from "../../lib/apiClient";
import { formatDate } from "../../lib/formatters";
import { getProjects, getReportById, submitReport, updateReport } from "./reports.api";

export function EditReportPage() {
  const { reportId = "" } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const formRef = useRef<HTMLFormElement>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const reportQuery = useQuery({ queryKey: ["report", reportId], queryFn: () => getReportById(reportId), enabled: Boolean(reportId) });
  const projectsQuery = useQuery({ queryKey: ["projects"], queryFn: getProjects });
  const report = reportQuery.data;
  const isArchived = report?.status === "ARCHIVED";
  const isDraft = report?.status === "DRAFT";

  function invalidate() {
    void queryClient.invalidateQueries({ queryKey: ["current-week-reports"] });
    void queryClient.invalidateQueries({ queryKey: ["my-reports"] });
    void queryClient.invalidateQueries({ queryKey: ["report", reportId] });
  }

  function buildPayload(form: HTMLFormElement) {
    const fd = new FormData(form);
    return {
      project_id: String(fd.get("project_id")),
      tasks_completed: String(fd.get("tasks_completed")),
      tasks_planned: String(fd.get("tasks_planned")),
      blockers: String(fd.get("blockers")) || null,
      hours_worked: fd.get("hours_worked") ? Number(fd.get("hours_worked")) : null,
      notes: String(fd.get("notes")) || null,
    };
  }

  async function save(thenSubmit: boolean) {
    const form = formRef.current;
    if (!form || busy) return;
    setBusy(true);
    setError("");
    try {
      await updateReport(reportId, buildPayload(form));
      if (thenSubmit) await submitReport(reportId);
      invalidate();
      navigate("/member/dashboard");
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm font-semibold text-violet-600">Weekly update</p>
            <h2 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">Edit Weekly Report</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">Update your completed work, plans, blockers, and hours.</p>
          </div>
          <Button variant="secondary" onClick={() => navigate(-1)}><ArrowLeft className="h-4 w-4" />Back</Button>
        </div>

        {reportQuery.isLoading && <LoadingSkeleton />}
        {reportQuery.isError && (
          <Card>
            <p className="font-semibold text-rose-700">Could not load this report.</p>
            <p className="mt-1 text-sm text-slate-500">It may not exist or you may not have access to it.</p>
          </Card>
        )}

        {report && (
          <Card className="overflow-hidden p-0">
            <div className="flex items-center justify-between gap-3 border-b border-slate-200 bg-gradient-to-r from-slate-950 to-violet-700 px-6 py-5 text-white">
              <div>
                <p className="text-sm font-semibold text-violet-100">Report details</p>
                <h3 className="mt-1 text-xl font-bold">Week {formatDate(report.week_start)} – {formatDate(report.week_end)}</h3>
              </div>
              <Badge value={report.is_late ? "LATE" : report.status} />
            </div>

            <form ref={formRef} onSubmit={(e) => { e.preventDefault(); save(false); }} className="space-y-6 p-6">
              {error && <div className="rounded-2xl bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700 ring-1 ring-rose-100">{error}</div>}
              {isArchived && <div className="rounded-2xl bg-amber-50 px-4 py-3 text-sm font-semibold text-amber-700 ring-1 ring-amber-100">Archived reports cannot be edited.</div>}

              <fieldset disabled={isArchived || busy} className="space-y-6">
                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <span className="mb-1.5 block text-sm font-semibold text-slate-700">Week</span>
                    <div className="flex h-11 items-center rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-500">{formatDate(report.week_start)} – {formatDate(report.week_end)}</div>
                  </div>
                  <label className="block md:col-span-2">
                    <span className="mb-1.5 block text-sm font-semibold text-slate-700">Project / Category</span>
                    <select name="project_id" required defaultValue={report.project.id} className="h-11 w-full rounded-2xl border border-slate-200 bg-white/90 px-4 text-sm text-slate-900 shadow-sm outline-none transition focus:border-violet-400 focus:ring-4 focus:ring-violet-100">
                      {projectsQuery.data?.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
                    </select>
                  </label>
                </div>

                <div className="grid gap-5 lg:grid-cols-2">
                  <Textarea label="Tasks completed" name="tasks_completed" defaultValue={report.tasks_completed} required />
                  <Textarea label="Tasks planned for next week" name="tasks_planned" defaultValue={report.tasks_planned} required />
                </div>
                <Textarea label="Blockers / challenges" name="blockers" defaultValue={report.blockers ?? ""} placeholder="Mention blockers, risks, dependencies..." />
                <div className="grid gap-4 md:grid-cols-2">
                  <Input label="Hours worked" name="hours_worked" type="number" min="0" max="168" step="0.5" defaultValue={report.hours_worked ?? ""} />
                  <Input label="Optional notes or links" name="notes" defaultValue={report.notes ?? ""} placeholder="PR links, documents, references..." />
                </div>

                <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
                  <Button type="button" variant="secondary" onClick={() => navigate(-1)}>Cancel</Button>
                  <Button type="submit" variant="secondary" isLoading={busy}><Save className="h-4 w-4" />Save changes</Button>
                  {isDraft && <Button type="button" isLoading={busy} onClick={() => save(true)}><Send className="h-4 w-4" />Save & submit</Button>}
                </div>
              </fieldset>
            </form>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
