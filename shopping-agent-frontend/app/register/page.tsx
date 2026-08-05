"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { registerUser, ApiError } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await registerUser({
        username,
        password,
        full_name: fullName || undefined,
        email: email || undefined,
      });
      router.push("/login?registered=1");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't create your account. Try again.");
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
          <h1 className="font-display text-3xl italic text-ink">Open a tab</h1>
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

          <div className="mb-5">
            <label htmlFor="fullName" className="block font-mono text-xs uppercase tracking-wide text-ink-soft mb-1.5">
              Full name <span className="normal-case text-hairline">(optional)</span>
            </label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full border border-hairline rounded-sm px-3 py-2 bg-paper focus:bg-white transition-colors"
              autoComplete="name"
            />
          </div>

          <div className="mb-5">
            <label htmlFor="email" className="block font-mono text-xs uppercase tracking-wide text-ink-soft mb-1.5">
              Email <span className="normal-case text-hairline">(optional)</span>
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-hairline rounded-sm px-3 py-2 bg-paper focus:bg-white transition-colors"
              autoComplete="email"
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
              autoComplete="new-password"
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
            {isSubmitting ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="text-center text-sm text-ink-soft mt-6">
          Already have a tab open?{" "}
          <Link href="/login" className="text-moss hover:text-moss-deep underline underline-offset-2">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  );
}
