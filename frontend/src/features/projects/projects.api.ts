import { apiClient } from "../../lib/apiClient";
import type { Project } from "../../types";

export interface ProjectPayload {
  name: string;
  description?: string | null;
  color?: string | null;
}

export async function listProjects(): Promise<Project[]> {
  const response = await apiClient.get<Project[]>("/projects");
  return response.data;
}
export async function createProject(payload: ProjectPayload): Promise<Project> {
  const response = await apiClient.post<Project>("/projects", payload);
  return response.data;
}
export async function updateProject(id: string, payload: ProjectPayload): Promise<Project> {
  const response = await apiClient.patch<Project>(`/projects/${id}`, payload);
  return response.data;
}
export async function archiveProject(id: string): Promise<void> {
  await apiClient.delete(`/projects/${id}`);
}
