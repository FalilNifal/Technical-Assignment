import { apiClient } from "../../lib/apiClient";
import type { AuthResponse, User } from "../../types";

export interface LoginPayload { email: string; password: string; }
export interface RegisterPayload { full_name: string; email: string; password: string; }
export async function login(payload: LoginPayload): Promise<AuthResponse> { const response = await apiClient.post<AuthResponse>("/auth/login", payload); return response.data; }
export async function register(payload: RegisterPayload): Promise<AuthResponse> { const response = await apiClient.post<AuthResponse>("/auth/register", payload); return response.data; }
export async function getCurrentUser(): Promise<User> { const response = await apiClient.get<User>("/auth/me"); return response.data; }
