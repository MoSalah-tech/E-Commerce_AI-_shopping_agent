"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { loginUser, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const { access_token } = await loginUser(username, password);
      login(access_token, username);
      router.push("/chat");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't sign in. Try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <p className="font-mono text-xs tracking-[0.2em] uppercase text-ink-soft mb-2">
            Cart &amp; Ledger
          </p>
          <h1 className="font-display text-3xl italic text-ink">Welcome back</h1>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-paper-raised border border-hairline rounded-sm p-8 ticket-edge pb-10 shadow-sm"
        >
          <div className="mb-5">
            <label htmlFor="username" className="block font-mono text-xs uppercase tracking-wide text-ink-soft mb-1.5">
              Username
            </label>
            <input
              id="username"
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-hairline rounded-sm px-3 py-2 bg-paper focus:bg-white transition-colors"
              autoComplete="username"
            />
          </div>

          <div className="mb-6">
            <label htmlFor="password" className="block font-mono text-xs uppercase tracking-wide text-ink-soft mb-1.5">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-hairline rounded-sm px-3 py-2 bg-paper focus:bg-white transition-colors"
              autoComplete="current-password"
            />
          </div>

          {error && (
            <p className="text-danger text-sm mb-4" role="alert">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-moss hover:bg-moss-deep text-paper font-medium py-2.5 rounded-sm transition-colors disabled:opacity-60"
          >
            {isSubmitting ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="text-center text-sm text-ink-soft mt-6">
          New here?{" "}
          <Link href="/register" className="text-moss hover:text-moss-deep underline underline-offset-2">
            Create an account
          </Link>
        </p>
      </div>
    </main>
  );
}
