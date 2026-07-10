import { apiClient } from "../../lib/apiClient";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  reply: string;
  tools_used: string[];
  model_name?: string | null;
  generated_by_fallback: boolean;
}

export async function sendChat(messages: ChatMessage[]): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>("/ai/chat", { messages });
  return response.data;
}
