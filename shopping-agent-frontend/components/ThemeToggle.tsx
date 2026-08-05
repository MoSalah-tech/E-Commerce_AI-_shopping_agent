"use client";

import { useTheme } from "@/lib/theme-context";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="font-mono text-[11px] uppercase tracking-wide text-ink-soft hover:text-moss transition-colors border border-hairline rounded-sm px-2.5 py-1.5"
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
    >
      {theme === "dark" ? "☀ Light" : "☾ Dark"}
    </button>
  );
}