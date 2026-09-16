import type { ReactNode } from "react";

import { GlobalSearchTrigger } from "@/components/layout/global-search-trigger";
import { LogoutButton } from "@/components/layout/logout-button";
import { MobileNav } from "@/components/layout/mobile-nav";
import { NavRail } from "@/components/layout/nav-rail";
import { ThemeToggle } from "@/components/layout/theme-toggle";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <NavRail />

      <div className="flex flex-1 flex-col min-w-0">
        <MobileNav />

        <header className="flex items-center justify-between gap-3 border-b border-border px-4 md:px-8 h-14 shrink-0">
          <span className="hidden lg:block font-mono text-xs text-muted-foreground tracking-wide shrink-0">
            NEXUS PERSONAL
          </span>
          <div className="flex flex-1 items-center justify-end gap-2 lg:justify-between">
            <GlobalSearchTrigger />
            <div className="flex items-center gap-1">
              <ThemeToggle />
              <LogoutButton />
            </div>
          </div>
        </header>

        <main className="flex-1 px-4 md:px-8 py-8">{children}</main>
      </div>
    </div>
  );
}
