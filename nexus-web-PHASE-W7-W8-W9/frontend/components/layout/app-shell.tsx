import type { ReactNode } from "react";

import { MobileNav } from "@/components/layout/mobile-nav";
import { NavRail } from "@/components/layout/nav-rail";
import { ThemeToggle } from "@/components/layout/theme-toggle";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <NavRail />

      <div className="flex flex-1 flex-col min-w-0">
        <MobileNav />

        <header className="flex items-center justify-between border-b border-border px-4 md:px-8 h-14 shrink-0">
          <span className="font-mono text-xs text-muted-foreground tracking-wide">
            NEXUS PERSONAL
          </span>
          <ThemeToggle />
        </header>

        <main className="flex-1 px-4 md:px-8 py-8">{children}</main>
      </div>
    </div>
  );
}
