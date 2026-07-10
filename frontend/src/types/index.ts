export type Role = "TEAM_MEMBER" | "MANAGER" | "ADMIN";
export type ReportStatus = "DRAFT" | "SUBMITTED" | "ARCHIVED" | "PENDING" | "LATE";

export interface User {
  id: string;
  full_name: string;
  email: string;
  role: Role;
  avatar_url?: string | null;
  is_active: boolean;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Project {
  id: string;
  name: string;
  description?: string | null;
  color?: string | null;
  is_active?: boolean;
}

export interface WeeklyReport {
  id: string;
  user_id: string;
  project: Project;
  week_start: string;
  week_end: string;
  tasks_completed: string;
  tasks_planned: string;
  blockers?: string | null;
  hours_worked?: string | number | null;
  notes?: string | null;
  status: ReportStatus;
  submitted_at?: string | null;
  is_late: boolean;
  created_at: string;
  updated_at: string;
}

export interface DashboardSummary {
  week_start: string;
  week_end: string;
  total_team_members: number;
  total_reports: number;
  submitted_reports: number;
  draft_reports: number;
  late_reports: number;
  pending_members: number;
  submission_percentage: number;
  blocker_count: number;
  total_hours_reported: string | number;
}

export interface ProjectDistributionItem {
  project_id: string;
  project_name: string;
  project_color?: string | null;
  report_count: number;
  submitted_count: number;
  blocker_count: number;
  total_hours: string | number;
}

export interface TeamPerformanceItem {
  member_id: string;
  member_name: string;
  member_email: string;
  report_count: number;
  submitted_count: number;
  draft_count: number;
  late_count: number;
  blocker_count: number;
  total_hours: string | number;
  submission_status: ReportStatus;
  last_submitted_at?: string | null;
}

export interface ActivityTimelineItem {
  id: string;
  type: string;
  title: string;
  description: string;
  actor_name?: string | null;
  project_name?: string | null;
  report_id?: string | null;
  created_at: string;
}

export interface TeamMemberItem {
  member_id: string;
  member_name: string;
  member_email: string;
}

export interface TeamReportItem {
  report_id: string;
  member_id: string;
  member_name: string;
  project_id: string;
  project_name: string;
  project_color?: string | null;
  week_start: string;
  week_end: string;
  tasks_completed: string;
  tasks_planned: string;
  blockers?: string | null;
  hours_worked?: string | number | null;
  notes?: string | null;
  status: ReportStatus;
  is_late: boolean;
  submitted_at?: string | null;
}
