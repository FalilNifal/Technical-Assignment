import { apiClient } from "../../lib/apiClient";
import type { Project, WeeklyReport } from "../../types";

export interface CreateReportPayload { project_id: string; week_start: string; week_end: string; tasks_completed: string; tasks_planned: string; blockers?: string | null; hours_worked?: number | null; notes?: string | null; }
export async function getProjects(): Promise<Project[]> { const response = await apiClient.get<Project[]>("/projects"); return Array.isArray(response.data) ? response.data : (response.data as any).projects ?? []; }
export async function getCurrentWeekReports(): Promise<{ week_start: string; week_end: string; reports: WeeklyReport[]; }> { const response = await apiClient.get("/reports/me/current"); return response.data; }
export async function getMyReports(): Promise<{ reports: WeeklyReport[]; total: number; }> { const response = await apiClient.get("/reports/me"); return response.data; }
export async function createReport(payload: CreateReportPayload): Promise<WeeklyReport> { const response = await apiClient.post<WeeklyReport>("/reports", payload); return response.data; }
export async function submitReport(reportId: string): Promise<{ id: string; status: string; submitted_at: string; is_late: boolean; }> { const response = await apiClient.post(`/reports/${reportId}/submit`); return response.data; }
export interface UpdateReportPayload { project_id?: string; tasks_completed?: string; tasks_planned?: string; blockers?: string | null; hours_worked?: number | null; notes?: string | null; }
export async function getReportById(reportId: string): Promise<WeeklyReport> { const response = await apiClient.get<WeeklyReport>(`/reports/${reportId}`); return response.data; }
export async function updateReport(reportId: string, payload: UpdateReportPayload): Promise<WeeklyReport> { const response = await apiClient.patch<WeeklyReport>(`/reports/${reportId}`, payload); return response.data; }
