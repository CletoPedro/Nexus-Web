"use client";

import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";

import { ApiError } from "@/lib/api/client";
import { authApi } from "@/lib/api/auth";
import type { CurrentUser } from "@/types/auth";

interface AuthContextValue {
  user: CurrentUser;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within <AuthGuard>");
  }
  return ctx;
}

/**
 * Wraps every protected route. Checks the session once on mount via
 * GET /auth/me (the cookie itself is httpOnly and invisible to this
 * code — we only ever learn whether it's valid by asking the backend).
 * Unauthenticated or expired sessions redirect to /login immediately,
 * per W12: "qualquer rota protegida deve redirecionar para /login."
 */
export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function check() {
      try {
        const me = await authApi.me();
        if (!cancelled) {
          setUser(me);
          setChecked(true);
        }
      } catch (err) {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 401) {
          router.replace("/login");
          return;
        }
        // Backend unavailable or another error — still send to /login
        // rather than showing broken protected content.
        router.replace("/login");
      }
    }
    check();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function logout() {
    try {
      await authApi.logout();
    } finally {
      router.replace("/login");
    }
  }

  if (!checked || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted-foreground">Loading your NEXUS…</p>
      </div>
    );
  }

  return <AuthContext.Provider value={{ user, logout }}>{children}</AuthContext.Provider>;
}
