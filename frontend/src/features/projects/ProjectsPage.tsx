import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FolderKanban, Pencil, Plus, Trash2, X } from "lucide-react";
import { AppShell } from "../../components/layout/AppShell";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { EmptyState } from "../../components/ui/EmptyState";
import { Input } from "../../components/ui/Input";
import { LoadingSkeleton } from "../../components/ui/LoadingSkeleton";
import { Textarea } from "../../components/ui/Textarea";
import { getApiErrorMessage } from "../../lib/apiClient";
import type { Project } from "../../types";
import { archiveProject, createProject, listProjects, updateProject } from "./projects.api";

const DEFAULT_FORM = { name: "", description: "", color: "#6366f1" };

export function ProjectsPage() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState(DEFAULT_FORM);
  const [editing, setEditing] = useState<Project | null>(null);
  const [error, setError] = useState("");

  const query = useQuery({ queryKey: ["manage-projects"], queryFn: listProjects });

  function invalidate() {
    void queryClient.invalidateQueries({ queryKey: ["manage-projects"] });
    void queryClient.invalidateQueries({ queryKey: ["projects"] });
    void queryClient.invalidateQueries({ queryKey: ["projects-list"] });
  }
  function resetForm() {
    setEditing(null);
    setForm(DEFAULT_FORM);
    setError("");
  }

  const saveMutation = useMutation({
    mutationFn: () => {
      const payload = { name: form.name.trim(), description: form.description.trim() || null, color: form.color || null };
      return editing ? updateProject(editing.id, payload) : createProject(payload);
    },
    onSuccess: () => { invalidate(); resetForm(); },
    onError: (err) => setError(getApiErrorMessage(err)),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => archiveProject(id),
    onSuccess: () => invalidate(),
    onError: (err) => setError(getApiErrorMessage(err)),
  });

  function startEdit(project: Project) {
    setEditing(project);
    setForm({ name: project.name, description: project.description ?? "", color: project.color ?? "#6366f1" });
    setError("");
  }
  function handleDelete(project: Project) {
    if (window.confirm(`Archive "${project.name}"? It will be hidden from new reports.`)) {
      deleteMutation.mutate(project.id);
    }
  }

  const projects = query.data ?? [];

  return (
    <AppShell>
      <div className="mx-auto max-w-5xl space-y-6">
        <div>
          <p className="text-sm font-semibold text-violet-600">Workspace admin</p>
          <h2 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">Manage <span className="text-aurora">Projects</span></h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">Add, edit, or archive the projects and categories that team members tag their reports with.</p>
        </div>

        {/* Add / edit form */}
        <Card>
          <div className="mb-4 flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 to-fuchsia-500 text-white shadow-glow-violet">
              {editing ? <Pencil className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
            </div>
            <h3 className="text-lg font-semibold text-slate-950">{editing ? `Edit "${editing.name}"` : "Add a project"}</h3>
          </div>
          {error && <div className="mb-4 rounded-2xl bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700 ring-1 ring-rose-100">{error}</div>}
          <form onSubmit={(e) => { e.preventDefault(); if (form.name.trim().length < 2) { setError("Name must be at least 2 characters."); return; } saveMutation.mutate(); }} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-[1fr_auto]">
              <Input label="Project name" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} placeholder="e.g. Marketing" required />
              <label className="block">
                <span className="mb-1.5 block text-sm font-semibold text-slate-700">Color</span>
                <input type="color" value={form.color} onChange={(e) => setForm((f) => ({ ...f, color: e.target.value }))} className="h-11 w-20 cursor-pointer rounded-2xl border border-slate-200 bg-white p-1" />
              </label>
            </div>
            <Textarea label="Description" value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} placeholder="What is this project about?" className="min-h-20" />
            <div className="flex justify-end gap-3">
              {editing && <Button type="button" variant="secondary" onClick={resetForm}><X className="h-4 w-4" />Cancel</Button>}
              <Button type="submit" isLoading={saveMutation.isPending}>{editing ? "Save changes" : "Add project"}</Button>
            </div>
          </form>
        </Card>

        {/* List */}
        {query.isLoading && <LoadingSkeleton />}
        {query.isError && <Card><p className="font-semibold text-rose-700">Could not load projects.</p></Card>}
        {query.data && projects.length === 0 && <EmptyState title="No projects yet" description="Add your first project above to get started." />}
        {projects.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-2">
            {projects.map((project) => (
              <Card key={project.id} className="flex items-start justify-between gap-4">
                <div className="flex min-w-0 items-start gap-3">
                  <span className="mt-1 h-10 w-10 shrink-0 rounded-2xl ring-1 ring-slate-900/5" style={{ background: project.color ?? "#e2e8f0" }} />
                  <div className="min-w-0">
                    <p className="flex items-center gap-2 font-semibold text-slate-950"><FolderKanban className="h-4 w-4 text-violet-500" />{project.name}</p>
                    <p className="mt-1 text-sm leading-6 text-slate-500">{project.description || "No description"}</p>
                  </div>
                </div>
                <div className="flex shrink-0 gap-1">
                  <button type="button" onClick={() => startEdit(project)} aria-label="Edit project" className="rounded-xl p-2 text-slate-400 transition hover:bg-violet-50 hover:text-violet-600"><Pencil className="h-4 w-4" /></button>
                  <button type="button" onClick={() => handleDelete(project)} aria-label="Archive project" className="rounded-xl p-2 text-slate-400 transition hover:bg-rose-50 hover:text-rose-600"><Trash2 className="h-4 w-4" /></button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
