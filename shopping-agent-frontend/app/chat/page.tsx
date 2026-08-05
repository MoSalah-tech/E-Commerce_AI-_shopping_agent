"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { sendChatMessage, listThreads, getThreadMessages, deleteThread,ThreadSummary, ApiError } from "@/lib/api";
import { ThreadSidebar } from "@/components/ThreadSidebar";
import { ChatMessage, Message } from "@/components/ChatMessage";
import { Recommendation } from "@/components/RecommendationCard";
import { ThemeToggle } from "@/components/ThemeToggle";

// Tries to pull a list of recommendation-like objects out of whatever
// shape `result.data` comes back as. Adjust this once the backend's
// actual agent output shape is confirmed.
type ExecuterOutputShape = {

  recommendation: Recommendation[];
  summary?: string;
}

function extractRecommendations(data: unknown): Recommendation[] | undefined {
  if (!data || typeof data !== "object") return undefined;
  const obj = data as ExecuterOutputShape;
  return Array.isArray(obj.recommendation) ? obj.recommendation : undefined;
}

function extractText(data: unknown): string | undefined {
  if (!data || typeof data !== "object") return undefined;
  const obj = data as ExecuterOutputShape;
  return typeof obj.summary === "string" ? obj.summary : undefined;
}

export default function ChatPage() {
  const router = useRouter();
  const { token, username, isLoading, logout } = useAuth();

  const [threads, setThreads] = useState<ThreadSummary[]>([]);
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isLoading && !token) router.push("/login");
  }, [isLoading, token, router]);

  useEffect(() => {
    if (token) refreshThreads();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function refreshThreads() {
    if (!token) return;
    try {
      const list = await listThreads(token);
      setThreads(list);
    } catch {
      // non-fatal -- sidebar just stays empty
    }
  }

  function handleNewChat() {
    setActiveThreadId(null);
    setMessages([]);
    setError(null);
  }


  async function handleSelectThread(id: string) {
    setActiveThreadId(id);
    setMessages([]);
    setError(null);
    if (!token) return;
    try {
      const history = await getThreadMessages(token, id);
      setMessages(
        history.map((m) => ({
          id: crypto.randomUUID(),
          role: m.role === "user" ? "user" : "assistant",
          text: m.content,
          recommendations: m.recommendations,
        }))
      );
    } catch {
      setError("Couldn't load that conversation's history.");
    }
  } 

  async function handleDeleteThread(id: string) {
    if (!token) return;
    const confirmed = window.confirm("Delete this conversation? This can't be undone.");
    if (!confirmed) return;

    try {
      await deleteThread(token, id);
      setThreads((prev) => prev.filter((t) => t.id !== id));
      if (activeThreadId === id) {
        setActiveThreadId(null);
        setMessages([]);
      }
    } catch {
      setError("Couldn't delete that conversation.");
    }
  }
  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || !token || isSending) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      text: input,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsSending(true);
    setError(null);

    try {
      const result = await sendChatMessage(token, userMessage.text!, activeThreadId);
      setActiveThreadId(result.thread_id);

      // run_agent() can return { success: false, error: "..." } (e.g. LLM/search
      // failure, or no recommendation generated) even on a 200 response.
      if (!result.success) {
        setError(result.error || "The agent couldn't complete that request.");
      } else {
        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          text: extractText(result.data),
          recommendations: extractRecommendations(result.data),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }
      refreshThreads();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong sending that.");
    } finally {
      setIsSending(false);
    }
  }

  if (isLoading || !token) return null;

  return (
    <div className="flex h-screen bg-paper">
      <ThreadSidebar
        threads={threads}
        activeThreadId={activeThreadId}
        onSelectThread={handleSelectThread}
        onNewChat={handleNewChat}
        onDeleteThread={handleDeleteThread}
        username={username}
        onLogout={() => {
          logout();
          router.push("/login");
        }}
      />

      <main className="flex-1 flex flex-col">
        <header className="border-b border-hairline px-8 py-5">
          <h1 className="font-display text-xl italic text-ink">
            {activeThreadId ? "Continuing your tab" : "New tab"}
          </h1>
        </header>

        <div className="flex-1 overflow-y-auto px-8 py-6 space-y-5">
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center">
              <p className="font-display text-lg italic text-ink-soft text-center max-w-sm">
                Tell me what you&apos;re shopping for, and I&apos;ll start a running tab of what I find.
              </p>
            </div>
          )}
          {messages.map((m) => (
            <ChatMessage key={m.id} message={m} />
          ))}
          {isSending && (
            <p className="font-mono text-xs text-ink-soft px-1">Checking the shelves…</p>
          )}
          {error && (
            <p className="text-danger text-sm" role="alert">
              {error}
            </p>
          )}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={handleSend} className="border-t border-hairline px-8 py-5 flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="What are you looking for?"
            className="flex-1 border border-hairline rounded-sm px-4 py-2.5 bg-paper-raised focus:bg-white transition-colors"
            disabled={isSending}
          />
          <button
            type="submit"
            disabled={isSending || !input.trim()}
            className="bg-moss hover:bg-moss-deep text-paper font-medium px-6 py-2.5 rounded-sm transition-colors disabled:opacity-60"
          >
            Send
          </button>
        </form>
      </main>
    </div>
  );
}
