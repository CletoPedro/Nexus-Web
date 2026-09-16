"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiError } from "@/lib/api/client";
import { authApi } from "@/lib/api/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await authApi.login(email.trim(), password);
      router.replace("/now");
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 422 || err.status === 401) {
          setError("Incorrect email or password.");
        } else if (err.status >= 500 || err.status === 0) {
          setError("NEXUS is unavailable right now. Try again in a moment.");
        } else {
          setError(err.message);
        }
      } else {
        setError("Could not reach NEXUS. Check your connection and try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <span className="font-display text-2xl tracking-tight">NEXUS</span>
          <p className="mt-1 font-mono text-xs text-muted-foreground tracking-wide">
            PERSONAL
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="flex flex-col gap-3 rounded-[var(--radius-md)] border border-border bg-card p-6"
        >
          <div>
            <label htmlFor="email" className="mb-1 block text-xs text-muted-foreground">
              Email
            </label>
            <Input
              id="email"
              type="email"
              autoFocus
              autoComplete="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="password" className="mb-1 block text-xs text-muted-foreground">
              Password
            </label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && (
            <p className="rounded-[var(--radius-sm)] border border-highlight/40 bg-highlight/10 px-3 py-2 text-sm text-highlight">
              {error}
            </p>
          )}

          <Button type="submit" disabled={isSubmitting} className="mt-2">
            {isSubmitting ? "Signing in…" : "Sign in"}
          </Button>
        </form>
      </div>
    </div>
  );
}
