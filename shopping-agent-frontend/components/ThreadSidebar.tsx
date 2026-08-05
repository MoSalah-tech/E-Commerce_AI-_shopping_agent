"use client";

import { ThreadSummary } from "@/lib/api";
import { ThemeToggle } from "./ThemeToggle";


export function ThreadSidebar({
  threads,
  activeThreadId,
  onSelectThread,
  onNewChat,
  onDeleteThread,
  username,
  onLogout,
}: {
  threads: ThreadSummary[];
  activeThreadId: string | null;
  onSelectThread: (id: string) => void;
  onNewChat: () => void;
  onDeleteThread: (id: string) => void;
  username: string | null;
  onLogout: () => void;
}) {
  return (
    <aside className="w-64 shrink-0 border-r border-hairline bg-paper-raised h-screen flex flex-col">
      <div className="p-5 border-b border-hairline flex items-center justify-between gap-2">
        <p className="font-mono text-[11px] tracking-[0.2em] uppercase text-ink-soft">
          Cart &amp; Ledger
        </p>
        <ThemeToggle />
      </div>
      <div className="p-3">
        <button
          onClick={onNewChat}
          className="w-full text-left px-3 py-2 rounded-sm border border-hairline hover:border-moss hover:text-moss transition-colors font-mono text-xs uppercase tracking-wide"
        >
          + New chat
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 space-y-1">
        {threads.length === 0 && (
          <p className="text-xs text-ink-soft px-2 py-4 italic font-display">
            No conversations yet.
          </p>
        )}
        {threads.map((thread) => (
          <div
            key={thread.id}
            className={`group flex items-center gap-1 rounded-sm transition-colors ${
              thread.id === activeThreadId ? "bg-moss/10" : "hover:bg-ink/5"
            }`}
          >
            <button
              onClick={() => onSelectThread(thread.id)}
              className={`flex-1 text-left px-3 py-2 text-sm truncate ${
                thread.id === activeThreadId ? "text-moss-deep font-medium" : "text-ink-soft"
              }`}
              title={thread.title || thread.id}
            >
              {thread.title || "Untitled conversation"}
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDeleteThread(thread.id);
              }}
              className="opacity-0 group-hover:opacity-100 px-2 py-2 text-ink-soft hover:text-danger transition-opacity font-mono text-xs"
              title="Delete conversation"
              aria-label={`Delete ${thread.title || "conversation"}`}
            >
              ✕
            </button>
          </div>
        ))}
      </nav>

      <div className="p-4 border-t border-hairline flex items-center justify-between">
        <span className="font-mono text-xs text-ink-soft truncate">{username}</span>
        <button
          onClick={onLogout}
          className="font-mono text-xs text-ink-soft hover:text-danger transition-colors"
        >
          Sign out
        </button>
      </div>
    </aside>
  );
}
