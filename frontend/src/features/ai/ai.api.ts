import { apiClient } from "../../lib/apiClient";

export interface GenerateTeamInsightsPayload {
  week_start: string;
  week_end: string;
  project_id?: string | null;
  member_id?: string | null;
}

export interface TeamInsightsResponse {
  id: string | null;
  insights: {
    summary: string;
    achievements: string[];
    blockers: string[];
    risks: string[];
    recommendations: string[];
  };
  context: {
    reports_used: number;
    week_start: string;
    week_end: string;
    project_id?: string | null;
    member_id?: string | null;
    model_name?: string | null;
    generated_by_fallback: boolean;
  };
  created_at?: string | null;
}

export async function generateTeamInsights(
  payload: GenerateTeamInsightsPayload
): Promise<TeamInsightsResponse> {
  const response = await apiClient.post<TeamInsightsResponse>("/ai/team-insights", payload);
  return response.data;
}
