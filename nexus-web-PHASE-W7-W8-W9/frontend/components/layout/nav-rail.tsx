"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { navModules } from "@/config/navigation";
import { cn } from "@/lib/utils";

/**
 * The left index rail. Modules read as tabs in a file drawer rather than
 * icon buttons in a dashboard: a solid vertical mark plus small-caps,
 * wide-tracked label marks the active module.
 */
export function NavRail() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="NEXUS modules"
      className="hidden md:flex w-56 shrink-0 flex-col border-r border-border bg-card"
    >
      <div className="px-5 pt-6 pb-4">
        <span className="font-display text-lg tracking-tight">NEXUS</span>
      </div>

      <ul className="flex flex-1 flex-col gap-0.5 px-2">
        {navModules.map((mod) => {
          const href = `/${mod.slug}`;
          const isActive =
            pathname === href || pathname.startsWith(`${href}/`);
          const Icon = mod.icon;

          return (
            <li key={mod.slug}>
              <Link
                href={href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  "group relative flex items-center gap-3 rounded-[var(--radius-sm)] px-3 py-2 text-sm transition-colors",
                  isActive
                    ? "text-foreground font-medium"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted",
                )}
              >
                {/* Active mark: the folder-tab signature */}
                <span
                  aria-hidden="true"
                  className={cn(
                    "absolute -left-2 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-full bg-accent transition-opacity",
                    isActive ? "opacity-100" : "opacity-0",
                  )}
                />
                <Icon className="size-4 shrink-0" />
                <span
                  className={cn(
                    isActive && "uppercase text-xs tracking-[0.08em]",
                  )}
                >
                  {mod.label}
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
