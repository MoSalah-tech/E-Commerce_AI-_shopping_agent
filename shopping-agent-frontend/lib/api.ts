// Central API client for talking to the FastAPI backend.
// Set NEXT_PUBLIC_API_URL in .env.local, e.g. http://127.0.0.1:8000

import { Recommendation } from "@/components/RecommendationCard";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function handle(res: Response) {
  if (!res.ok) {
    let detail = "Something went wrong. Please try again.";
    try {
      const body = await res.json();
      detail = body.detail || body.error || detail;
    } catch {
      // ignore parse errors, use default message
    }
    throw new ApiError(res.status, detail);
  }
  return res.json();
}

export async function registerUser(data: {
  username: string;
  password: string;
  full_name?: string;
  email?: string;
}) {
  const res = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handle(res);
}

export async function loginUser(username: string, password: string) {
  const form = new URLSearchParams();
  form.set("username", username);
  form.set("password", password);

  const res = await fetch(`${API_URL}/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString(),
  });
  return handle(res) as Promise<{ access_token: string; token_type: string }>;
}

export type ChatResponse = {
  success: boolean;
  thread_id: string;
  data?: unknown;
  error?: string;
};

export async function sendChatMessage(
  token: string,
  message: string,
  threadId?: string | null
) {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      message,
      ...(threadId ? { thread_id: threadId } : {}),
    }),
  });
  return handle(res) as Promise<ChatResponse>;
}

export type ThreadSummary = {
  id: string;
  title: string | null;
  created_at: string;
};

export async function listThreads(token: string) {
  const res = await fetch(`${API_URL}/chat/threads`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const body = await handle(res);
  return (body.data as ThreadSummary[]) || [];
}




export type ChatHistoryMessage = {
  role: string;
  content: string;
  recommendations?: Recommendation[];
};

export async function getThreadMessages(token: string, threadId: string) {
  const res = await fetch(`${API_URL}/chat/threads/${threadId}/messages`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const body = await handle(res);
  return (body.data as ChatHistoryMessage[]) || [];
}


export async function deleteThread(token: string, threadId: string) {
  const res = await fetch(`${API_URL}/chat/threads/${threadId}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  return handle(res);
}