import { apiClient } from "../../lib/apiClient";
import type {
  ActivityTimelineItem,
  DashboardSummary,
  ProjectDistributionItem,
  TeamMemberItem,
  TeamPerformanceItem,
  TeamReportItem,
} from "../../types";

export interface DashboardFilters {
  week_start?: string;
  week_end?: string;
  project_id?: string;
  member_id?: string;
}

function toParams(filters: DashboardFilters = {}): Record<string, string> {
  const params: Record<string, string> = {};
  if (filters.week_start) params.week_start = filters.week_start;
  if (filters.week_end) params.week_end = filters.week_end;
  if (filters.project_id) params.project_id = filters.project_id;
  if (filters.member_id) params.member_id = filters.member_id;
  return params;
}

export async function getDashboardSummary(filters: DashboardFilters = {}): Promise<DashboardSummary> {
  const response = await apiClient.get<DashboardSummary>("/dashboard/summary", { params: toParams(filters) });
  return response.data;
}
export async function getProjectDistribution(filters: DashboardFilters = {}): Promise<{ items: ProjectDistributionItem[] }> {
  const response = await apiClient.get("/dashboard/project-distribution", { params: toParams(filters) });
  return response.data;
}
export async function getTeamPerformance(filters: DashboardFilters = {}): Promise<{ items: TeamPerformanceItem[] }> {
  const response = await apiClient.get("/dashboard/team-performance", { params: toParams(filters) });
  return response.data;
}
export async function getActivityTimeline(filters: DashboardFilters = {}): Promise<{ items: ActivityTimelineItem[] }> {
  const response = await apiClient.get("/dashboard/activity", { params: toParams(filters) });
  return response.data;
}
export async function getTeamMembers(): Promise<{ items: TeamMemberItem[] }> {
  const response = await apiClient.get("/dashboard/members");
  return response.data;
}
export async function getTeamReports(filters: DashboardFilters = {}): Promise<{ items: TeamReportItem[]; total: number }> {
  const response = await apiClient.get("/dashboard/reports", { params: toParams(filters) });
  return response.data;
}
